from celery import Celery
from PIL import Image
from utils import utils_image
from dotenv import load_dotenv
from database.connection import SessionLocal, engine
from database import crud
from sqlalchemy.orm import Session
from schemas.schema import ImageProduct
from logger.logging_config import setup_logging
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

logger = setup_logging(__name__)

# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)

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
    task_always_eager=True,  # Executa as tasks de forma síncrona
    task_eager_propagates=True,  # Propaga exceções para fácil depuração
    task_default_queue='default',
    worker_hijack_root_logger=False,
)

@app.on_after_configure.connect
def configure_task_logger(sender=None, **kwargs):
    logger.propagate = False


@app.task
def identify_clothes(id_client, image_paths):
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
        # TRATAR
        pass

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
                logger.error("Segmentation failed.")
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

        # Uma vez finalizado o looping, implementar um alerta por e-mail.
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
def object_detection(image, object_type):
    category_to_detect = {'category_to_detect':object_type}

    with open(image, "rb") as image_file:
        files = {"image": (image, image_file, utils_image.get_mime_type(image))}

        response = requests.post(f"{MODELS_URI}/object_detection",
                            files=files,
                            data=category_to_detect,
                            headers=HEADER)
    
    return response

@app.task
def face_detection(image_b64: str, images_to_search_b64: str):
    image = utils_image.convert_base64_to_bytesIO(image_b64)
    images_to_search = utils_image.convert_base64_to_bytesIO(images_to_search_b64)

    files = {"image": ('faceid.jpeg', 
                       image,
                       utils_image.get_mime_type('faceid.jpeg')),
            "images_to_search" : ('unknown_face.jpeg',
                                  images_to_search,
                                  utils_image.get_mime_type(
                                      'unknown_face.jpeg'))}

    response = requests.post(f"{MODELS_URI}/face_detection",
                        files=files,
                        headers=HEADER)
    return response

@app.task
def image_segmentation(image_b64: str):
    image = utils_image.convert_base64_to_bytesIO(image_b64)
    files = {"image": ('segmentation.jpeg', 
                       image, 
                       utils_image.get_mime_type('segmentation.jpeg'))}
    
    response = requests.post(f"{MODELS_URI}/clothes_segmentation",
                            files=files,
                            headers=HEADER)

    return response

@app.task
def image_classification(subcategories, image_b64, file_name):
    image = utils_image.image_base64_to_buffer(image_b64)
    categories = {'categories_dict': json.dumps(subcategories)}

    files = {"image": (file_name, 
                       image, 
                       utils_image.get_mime_type(file_name))}

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