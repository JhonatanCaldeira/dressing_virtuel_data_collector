from colorsys import rgb_to_hsv
from http.client import HTTPResponse
from celery import Celery
from PIL import Image
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from utils import utils_image
from dotenv import load_dotenv
from database.connection import SessionLocal
from database import crud
from schemas.schema import ImageProduct
from logger.logging_config import setup_logging
from requests.auth import HTTPBasicAuth
import pandas as pd
import requests
import json
import os

load_dotenv(dotenv_path="config/.env")

# Define the path where the fashion dataset is stored
IMAGE_STORAGE_DIR = os.getenv("IMAGE_STORAGE_DIR")
BROKER_SERVER = os.getenv("BROKER_SERVER")

#DB
SERVER = os.getenv("PG_API_SERVER")
PORT = os.getenv("PG_API_PORT")
ENDPOINT = os.getenv("PG_API_ENDPONT")

PG_URI = f"http://{SERVER}:{PORT}/{ENDPOINT}"
PG_API_KEY = os.getenv("PG_API_KEY")

#MODELs
SERVER = os.getenv("MODELS_API_SERVER")
PORT = os.getenv("MODELS_API_PORT")
ENDPOINT = os.getenv("MODELS_API_ENDPOINT")

MODELS_URI = f"http://{SERVER}:{PORT}/{ENDPOINT}"
MODELS_API_KEY = os.getenv("MODELS_API_KEY")
HEADER = {"access_token": MODELS_API_KEY }

# METEO API
METEO_URI_TOKEN = os.getenv("METEO_URI_TOKEN")
METEO_URI_API = os.getenv("METEO_API_ENDPOINT")
METEO_USER = os.getenv("METEO_API_USER")
METEO_PASSWORD = os.getenv("METEO_API_PASSWORD")

#GEO API
GEOCO_API_ENDPOINT = os.getenv("GEOCO_API_ENDPOINT")
GEOCO_API_KEY = os.getenv("GEOCO_API_KEY")

# Neutral colors (RGB)
NEUTRAL_COLORS = [
    (0, 0, 0),       # Black
    (255, 255, 255), # White
    (128, 128, 128), # Gray
    (192, 192, 192), # Navy light
    (245, 245, 220), # Navy
]

logger = setup_logging(__name__)

def get_db():
    """
    Provides a database session to interact with the database during the request lifecycle.
    Closes the session after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = Celery('tasks', broker=f"amqp://{BROKER_SERVER}")

app.conf.update(
    task_always_eager=True,  # Synchonous tasks
    task_eager_propagates=True,  # Propagate exceptions
    task_default_queue='default',
    worker_hijack_root_logger=False,
)

@app.on_after_configure.connect
def configure_task_logger(sender=None, **kwargs):
    logger.propagate = False

@app.task
def identify_clothes(id_client, image_paths):
    """
    Task to identify clothes in images uploaded by clients.

    The task does the following:
    1. Loads categories (genders, seasons, colors, etc.) from the API.
    2. For each image provided by the client:
        a. Extracts each person present in the image.
        b. Identifies the client based on its Face ID.
        c. Extracts each piece of cloth weared by the client.
        d. Classifies each piece of cloth.
        e. Saves the images in the client directory.
        f. Saves the image path + categories in the DB.
    """
    logger.debug(f"Task started for client ID: {id_client}")

    # Load Categories
    dict_genders = get_categories('genders','gender')
    dict_seasons = get_categories('seasons','name')
    dict_colors = get_categories('colors','name')
    dict_usage = get_categories('usage_types','name')
    dict_article = get_categories('article_types','name')

    dict_of_dict_categories = {
        'id_gender': dict_genders,
        'id_season': dict_seasons,
        'id_color': dict_colors,
        'id_usagetype': dict_usage,
        'id_articletype': dict_article     
    }

    dict_of_categories = {
        'id_gender': list(dict_genders.keys()),
        'id_season': list(dict_seasons.keys()),
        'id_color': list(dict_colors.keys()),
        'id_usagetype': list(dict_usage.keys()),
        'id_articletype': list(dict_article.keys())
    }

    # Get Base 64 Client Face ID
    face_id = get_faceid(id_client)
    if face_id.status_code != 200:
        logger.error(f"Failed to get face ID for client ID {id_client}: {face_id.status_code}")
        raise HTTPException(
            status_code=403,
            detail=f"Unable to identify your FaceId, did you register it?")

    face_id_b64 = json.loads(face_id.content)['images']

    # For each image provided by the client:
    for image_path in image_paths:
        logger.debug(f"Processing image: {image_path}")

        # Extract each person present in the image.
        obj_response = object_detection(image_path,'person')

        if obj_response.status_code != 200:
            logger.warning(f"Object detection failed for image: {image_path}")
            continue

        data_obj_detection = json.loads(obj_response.content)

        for image_base64 in data_obj_detection['images']:
            # For each person identify the client based in its FaceID
            face_response = face_detection(face_id_b64, 
                                           image_base64)

            if face_response.status_code != 200:
                logger.warning(f"Face detection failed for image: {image_path}")
                continue

            data_face_detection = json.loads(face_response.content)
            face_detection_b64 = data_face_detection['images']
            # Once the client have been detected in the image
            # Extract each piece of cloth weared by the client
            segment_response = image_segmentation(face_detection_b64)

            if segment_response.status_code != 200:
                logger.error(f"Segmentation failed, for client ID {id_client}")
                continue

            data_segmentation = json.loads(segment_response.content)

            for img_segmentation_b64 in data_segmentation['images']:
                # Classify each piece of cloth
                image_name = utils_image.generate_image_name()
                classification_response = image_classification(
                    dict_of_categories, 
                    img_segmentation_b64, 
                    image_name)
                
                if classification_response.status_code != 200:
                    continue

                # Save the images in the client directory
                # Save the image path + categories in the DB
                image_bytes = utils_image.convert_base64_to_bytesIO(img_segmentation_b64)
                image_buffer = Image.open(image_bytes)
                if image_buffer.mode == 'RGBA':
                        image_buffer = image_buffer.convert('RGB')
                        
                image_new_path = IMAGE_STORAGE_DIR + '/' + str(id_client) + '/' + image_name
                image_buffer.save(image_new_path, format='JPEG')
                image_buffer.close()

                data_classification = json.loads(classification_response.content)

                image_product = {}
                image_product['id'] = None
                image_product['path'] = image_new_path
                image_product['id_client'] = id_client

                for key, value in data_classification.items():
                    image_product[key] = dict_of_dict_categories[key][value]

                new_image_product = crud.create_image_product(next(get_db()),
                                                              ImageProduct(**image_product))
                
        # Remove tmp images
        for image_path in image_paths:
            os.remove(image_path)

    logger.debug(f"Task completed for client ID: {id_client}")
    #Add function to alert the client by mail
    return True

@app.task
def get_categories(method, key):
    """
    Fetches categories (like gender, color, season, etc.) from the API.

    Args:
        method (str): API method to fetch (e.g., 'genders', 'colors').
        key (str): The key to extract from the API response (e.g., 'name', 'id').

    Returns:
        dict: A dictionary with category names as keys and their 
        corresponding IDs as values.
    """
    header = {"access_token":PG_API_KEY}
    response = requests.get(f"{PG_URI}/{method}",headers=header)
    dict = {x[key]: x['id'] for x in response.json()}

    return dict

@app.task
def object_detection(image_path: str, object_type: str):
    """
    Perform object detection on the given image and detect the given object type.

    Args:
        image_path (str): The path to the image to detect the object in.
        object_type (str): The type of object to detect.

    Returns:
        The response of the object detection API call.
    """
    # Set the category to detect
    category_to_detect = {'category_to_detect': object_type}

    # Open the image file in binary mode
    with open(image_path, "rb") as image_file:
        # Create the payload with the file
        files = {"image": (image_path, image_file, utils_image.get_mime_type(image_path))}

        # Perform the object detection
        response = requests.post(f"{MODELS_URI}/object_detection",
                            files=files,
                            data=category_to_detect,
                            headers=HEADER)
    
    # Return the response
    return response

@app.task
def face_detection(image_b64: str, images_to_search_b64: str):
    """
    Perform face detection on a base64 encoded image and a set of base64
    encoded images to search for the face.

    Args:
        image_b64 (str): The base64 encoded image to detect the face in.
        images_to_search_b64 (str): The base64 encoded images to search for the
            face in.

    Returns:
        requests.Response: The response from the face detection model.
    """
    # Convert the base64 encoded images to bytesIO objects
    image = utils_image.convert_base64_to_bytesIO(image_b64)
    images_to_search = utils_image.convert_base64_to_bytesIO(images_to_search_b64)

    # Create a dictionary with the image file for the request
    files = {"image": ('faceid.jpeg',
                       image,
                       utils_image.get_mime_type('faceid.jpeg')),
            "images_to_search" : ('unknown_face.jpeg',
                                  images_to_search,
                                  utils_image.get_mime_type(
                                      'unknown_face.jpeg'))}

    # Perform the face detection
    response = requests.post(f"{MODELS_URI}/face_detection",
                        files=files,
                        headers=HEADER)

    return response

@app.task
def image_segmentation(image_b64: str):
    """
    Perform image segmentation on a base64 encoded image, which is
    passed as a string.

    Args:
        image_b64 (str): The base64 encoded image as a string.

    Returns:
        str: The response from the segmentation model as a string.
    """
    image = utils_image.convert_base64_to_bytesIO(image_b64)

    # Create a dictionary with the image file for the request
    files = {"image": ('segmentation.jpeg', 
                       image, 
                       utils_image.get_mime_type('segmentation.jpeg'))}
    
    # Post the image to the segmentation model
    response = requests.post(f"{MODELS_URI}/clothes_segmentation",
                            files=files,
                            headers=HEADER)

    # Return the response from the segmentation model
    return response

@app.task
def image_classification(subcategories, image_b64, file_name):
    """
    Evaluates the similarity between an image and a dict of subcategory 
    descriptions using CLIP.

    Args:
        subcategories (dict): A dictionary with subcategory descriptions as
            values.
        image_b64 (str): The image to classify as a base64 encoded string.
        file_name (str): The name of the file to send in the request.

    Returns:
        response: The response from the API as a requests.Response object.
    """
    image = utils_image.image_base64_to_buffer(image_b64)
    categories = {'categories_dict': json.dumps(subcategories)}

    # Create a tuple with the file name, image buffer, and the MIME type of the 
    # image
    files = {"image": (file_name, 
                       image, 
                       utils_image.get_mime_type(file_name))}

    # Create the payload with the file and the categories dictionary
    response = requests.post(f"{MODELS_URI}/image_classification",
                        files=files,
                        data=categories,
                        headers=HEADER)
    
    return response

@app.task
def get_faceid(client_id):
    header = {"access_token": PG_API_KEY}
    response = requests.get(f"{PG_URI}/get_faceid?id_client={client_id}",
                             headers=header)
    
    return response

@app.task
def get_lat_long(address):
    """
    Gets the latitude and longitude of a given address from the geocoding API.

    Args:
        address (str): The address to get the coordinates for.

    Returns:
        dict: A dictionary containing the latitude and longitude of the address.
    """
    # Construct the URL
    url = f"{GEOCO_API_ENDPOINT}search?q={address},&api_key={GEOCO_API_KEY}"

    # Get the response
    response = requests.get(url)

    # Check if the response was successful
    if response.status_code == 200:
        # Return the coordinates
        return {'lat':response.json()[0]['lat'], 
                'long':response.json()[0]['lon']}
    else:
        # Raise an exception if the response was not successful
        raise HTTPException(
                status_code=403, 
                detail="Could not get Latitude and Longitude"
            )

@app.task
def get_meteo(datetime, lat, long, parameters = 't_2m:C', format = 'json'):
    """
    Gets weather data from the meteo API.
    
    Args:
        datetime (str): Date and time in ISO format (YYYY-MM-DDTHH:MM:SSZ).
        lat (str): Latitude of the location.
        long (str): Longitude of the location.
        parameters (str, optional): Parameters to retrieve from the API (default is 't_2m:C').
        format (str, optional): Format of the response (default is 'json').
    
    Returns:
        response (requests.Response): Response from the API.
    """
    # Get the access token
    response = requests.get(METEO_URI_TOKEN, 
                            auth=HTTPBasicAuth(METEO_USER, METEO_PASSWORD))

    if response.status_code == 200:
        access_token = response.json()['access_token']
    else:
        raise HTTPException(
                status_code=403, 
                detail="Could not validate API KEY"
            )

    # Construct the URL
    locations = f'{lat},{long}'
    url = f'{METEO_URI_API}/{datetime}/{parameters}/{locations}/{format}'
    
    # Set the header
    header = {'Authorization':f'Bearer {access_token}'}
    
    # Get the data
    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return response
    else:
        raise HTTPException(
                status_code=403, 
                detail="Could not get Meteo data"
            )

def find_matching_colors_df(df, base_color, mode='complementary'):
    """
    Finds colors that match the base color in a DataFrame, including neutral colors.
    
    Args:
        df (pd.DataFrame): DataFrame containing a 'color_rgb' column with colors in RGB format (R, G, B).
        base_color (tuple or str): Base color in RGB format (R, G, B) or as a string (e.g., "Grey Melange").
        mode (str): Matching mode ('complementary', 'analogous', 'triadic').
    
    Returns:
        pd.DataFrame: Filtered DataFrame with matching colors.
    """
    # Convert the base color to HSV
    base_h, base_s, base_v = rgb_to_hsv(*[x / 255.0 for x in eval(base_color)])
    
    # Define harmony based on the selected mode
    match_hues = []
    if mode == 'complementary':
        match_hues = [(base_h + 0.5) % 1]  # Opposite color
    elif mode == 'analogous':
        match_hues = [(base_h - 0.1) % 1, (base_h + 0.1) % 1]  # Adjacent colors
    elif mode == 'triadic':
        match_hues = [(base_h + 1/3) % 1, (base_h + 2/3) % 1]  # Triadic colors
    else:
        raise ValueError("Invalid mode. Choose 'complementary', 'analogous', or 'triadic'.")
    
    # Helper function to check if a color matches
    def color_matches(row):
        r, g, b = eval(row['color_rgb'])  # Convert string to tuple (R, G, B)
        # Check if the color is neutral
        if (r, g, b) in NEUTRAL_COLORS:
            return True
        # Calculate HSV and check harmony
        h, s, v = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return any(abs(h - target_h) < 0.05 for target_h in match_hues)
    
    # Apply the filter to the DataFrame
    filtered_df = df[df.apply(color_matches, axis=1)]
    
    return filtered_df


@app.task
def get_cloth_suggestion(id_client, season=None, temperature=None,
                         usage_type=None, id_top=None, id_bottom=None,
                         n_suggestions=3):
    """
    Provides clothing suggestions for a client based on the season, temperature,
    and usage type. Matches topwear and bottomwear based on color compatibility.

    Args:
        id_client (int): The client ID.
        season (optional, list or str): Season(s) for the clothing suggestion.
        temperature (optional, float): Current temperature to determine the season.
        usage_type (optional, str): Type of usage for filtering clothes.
        id_top (optional, int): Specific topwear ID to search a matching bottomwear.
        id_bottom (optional, int): Specific bottomwear ID to search a matching topwear.
        n_suggestions (int): Number of clothing suggestions to provide.

    Returns:
        dict: A dictionary with client ID and matching clothes suggestions.

    Raises:
        HTTPException: If neither season nor temperature is provided, 
                       if no images can be retrieved for the client,
                       or if no matching clothes are found.
    """

    # Determine the season based on the temperature if not provided
    season = define_season(season, temperature)
    if season is None:
            raise HTTPException(
            status_code=403,
            detail="Season or temperature must be provided"
        )

    # Access the client's images from the server
    header = {"access_token": PG_API_KEY}
    response = requests.get(f"{PG_URI}/images_from_client?client_id={id_client}",
                            headers=header)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=403,
            detail="Could not get images from client"
        )

    # Load the response data into a DataFrame and filter by season
    ds = pd.read_json(json.dumps(response.json()))
    ds = ds[ds['season'].isin(season)]

    # Further filter by usage type if provided
    if usage_type:
        ds = ds[ds['usage_type'] == usage_type]

    id_image = None
    random_match = False

    # Check if user selected a specific topwear or bottomwear
    if id_top:
        id_image = id_top
        subcaterogy_to_search = 'Bottomwear'
    elif id_bottom:
        id_image = id_bottom
        subcaterogy_to_search = 'Topwear'
    else:
        random_match = True

    matchs = {'id_client': id_client, 'matchs': []}
    if temperature is not None:
        matchs['temperature'] = temperature

    if len(ds) == 0:
        raise HTTPException(
            status_code=403,
            detail="No clothes fully matching the criteria"
        )

    # Generate clothing suggestions
    for _ in range(n_suggestions):
        if random_match:
            # Select a random topwear if no specific items are given
            topwear_random = ds[ds['sub_category'] == 'Topwear'].sample(n=1)
            id_image = topwear_random['id'].values[0]
            subcaterogy_to_search = 'Bottomwear'

        # Select the main image and search for matching subcategory
        ds_main_image = ds[ds['id'] == id_image]
        ds_to_search = ds[ds['sub_category'] == subcaterogy_to_search]

        # Find matching colors
        ds_matching = find_matching_colors_df(ds_to_search,
                                              ds_main_image['color_rgb'].values[0])

        if len(ds_matching) != 0:
            new_matching = {}
            if subcaterogy_to_search == 'Bottomwear':
                new_matching = {'id_top': int(id_image), 'id_bottom': int(ds_matching['id'].values[0])}
            else:
                new_matching = {'id_top': int(ds_matching['id'].values[0]), 'id_bottom': int(id_image)}

            matchs['matchs'].append(new_matching)

    if len(matchs['matchs']) == 0:
        raise HTTPException(
            status_code=403,
            detail="No matching found"
        )

    return JSONResponse(
        content=matchs, status_code=200, media_type="application/json"
    ) if matchs else JSONResponse(content="No matches found", status_code=404) 

def define_season(season, temperature):
    if season:
        if isinstance(season, str):
            season = [season]
    elif temperature:
        if temperature < 10:
            season = ['Winter']
        elif 10 <= temperature < 20:
            season = ['Fall', 'Spring']
        else:
            season = ['Summer']
    else:
        season = None
        
    return season
    