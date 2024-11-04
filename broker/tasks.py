from celery import Celery
from PIL import Image
import requests
import json
import mimetypes
import io, zipfile
import os
import time
import base64


from dotenv import load_dotenv
load_dotenv(dotenv_path="config/.env")

# Define the path where the fashion dataset is stored
IMAGE_TMP_DIR = os.getenv("IMAGE_TMP_DIR")
BROKER_SERVER = os.getenv("BROKER_SERVER")

SERVER = os.getenv("PG_API_SERVER")
PORT = os.getenv("PG_API_PORT")
ENDPOINT = os.getenv("PG_API_ENDPONT")

PG_URI = f"http://{SERVER}:{PORT}/{ENDPOINT}"
PG_API_KEY = os.getenv("PG_API_KEY")

#OBJECT DETECTION
SERVER = os.getenv("OBJ_DETECTION_API_SERVER")
PORT = os.getenv("OBJ_DETECTION_API_PORT")
ENDPOINT = os.getenv("OBJ_DETECTION_API_ENDPOINT")

OBJ_DETECTION_URI = f"http://{SERVER}:{PORT}/{ENDPOINT}"
OBJ_DETECTION_API_KEY = os.getenv("OBJ_DETECTION_API_KEY")

#FACE RECOGINITION
SERVER = os.getenv("FACE_RECOGNITION_API_SERVER")
PORT = os.getenv("FACE_RECOGNITION_API_PORT")
ENDPOINT = os.getenv("FACE_RECOGNITION_API_ENDPOINT")

FACE_RECOGNITION_URI = f"http://{SERVER}:{PORT}/{ENDPOINT}"
FACE_RECOGNITION_API_KEY = os.getenv("FACE_RECOGNITION_API_KEY")

#SEGMENTATION
SERVER = os.getenv("SEGMENTATION_API_SERVER")
PORT = os.getenv("SEGMENTATION_API_PORT")
ENDPOINT = os.getenv("SEGMENTATION_API_ENDPOINT")

SEGMENTATION_URI = f"http://{SERVER}:{PORT}/{ENDPOINT}"
SEGMENTATION_API_KEY = os.getenv("SEGMENTATION_API_KEY")

#CLASSIFICATION
SERVER = os.getenv("CLASSIFICATION_API_SERVER")
PORT = os.getenv("CLASSIFICATION_API_PORT")
ENDPOINT = os.getenv("CLASSIFICATION_API_ENDPOINT")

CLASSIFICATION_URI = f"http://{SERVER}:{PORT}/{ENDPOINT}"
CLASSIFICATION_API_KEY = os.getenv("CLASSIFICATION_API_KEY")

app = Celery('tasks', broker=f"amqp://{BROKER_SERVER}")

app.conf.update(
    task_always_eager=True,  # Executa as tasks de forma síncrona
    task_eager_propagates=True,  # Propaga exceções para fácil depuração
)

@app.task
def identify_clothes(id_client, image_paths):
    dict_genders = get_categories('genders','gender')
    dict_seasons = get_categories('seasons','name')
    dict_colors = get_categories('colors','name')
    dict_usage = get_categories('usage_types','name')
    dict_article = get_categories('article_types','name')

    dict_of_categories = {
        'gender': list(dict_genders.keys()),
        'season': list(dict_seasons.keys()),
        'color': list(dict_colors.keys()),
        'usage': list(dict_usage.keys()),
        'article': list(dict_article.keys())
    }

    for image_path in image_paths:

        obj_response = object_detection(image_path,'person')

        # Check if the response is OK
        if not obj_response.ok:
            #TRATAR
            continue

        #Implementar o GET da imagem base64 que está na DB
        face_id = get_faceid(id_client)
        face_response = face_detection(face_id, io.BytesIO(obj_response.content))

        if not face_response.ok:
            #TRATAR
            continue
        
        image = Image.open(io.BytesIO(face_response.content))
        timestamp = int(time.time())
        image_name =  f"{id_client}_face_{timestamp}.jpg"
        face_image_path = IMAGE_TMP_DIR + "/" + image_name
        image.save(face_image_path)

        segmentation_response = image_segmentation(face_image_path)

        os.remove(face_image_path)

        # Check if the response is OK
        if segmentation_response.ok:
            # Read the ZIP archive from the response content
            zip_file = zipfile.ZipFile(io.BytesIO(segmentation_response.content))
            
            # Extract and display each image
            for file_name in zip_file.namelist():
                # Open the image from the ZIP file
                with zip_file.open(file_name) as image_file:
                    print('Extracting the categories from the cropped image ...')

                    # Convert the image into an in-memory binary file
                    # Create a bytes buffer
                    img_byte_arr = io.BytesIO()  
                    # Save the image in JPEG format in the buffer
                    image.save(img_byte_arr, format='JPEG') 
                    # Go back to the start of the BytesIO buffer 
                    img_byte_arr.seek(0)  

                    # Perform CLIP evaluation to get the best 
                    # matching category for each attribute
                    selected_categories = image_classification(
                        dict_of_categories,
                        img_byte_arr)

                    #Implementar armazenamento na base de dados.
                    print(f"path: {image_file}")
                    print(selected_categories)

        # Excluir todas as imagens desnecessárias
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
def object_detection(image_path, object_type):
    header = {"access_token": OBJ_DETECTION_API_KEY }
    category_to_detect = {'category_to_detect':object_type}

    with open(image_path, "rb") as image_file:
        files = {"image": (image_path, image_file, get_mime_type(image_path))}

        response = requests.post(f"{OBJ_DETECTION_URI}/crop_detection",
                            files=files,
                            data=category_to_detect,
                            headers=header)
    
    return response

@app.task
def face_detection(image_path, zip_file):
    header = {"access_token":FACE_RECOGNITION_API_KEY}

    zip_file_content = base64.b64decode(zip_file)
    zip_file = io.BytesIO(zip_file_content)  # Converte de volta para BytesIO

    with open(image_path, "rb") as image_file:
            files = {"image": (image_path, image_file, get_mime_type(image_path)),
                    "images_to_search" : ('archive.zip', zip_file , "application/x-zip-compressed")}

            response = requests.post(f"{FACE_RECOGNITION_URI}/face_detection",
                                files=files,
                                headers=header)
    
    return response

@app.task
def image_segmentation(image_path):
    header = {"access_token":SEGMENTATION_API_KEY}
    
    with open(image_path, "rb") as image_file:
        files = {"image": (image_path, image_file, get_mime_type(image_path))}
        
        response = requests.post(f"{SEGMENTATION_URI}/crop_fullbody_clothes",
                                files=files,
                                headers=header)

    return response

@app.task
def image_classification(subcategories, image_path, file_name):

    header = {"access_token": CLASSIFICATION_API_KEY}
    categories = {'categories_dict': json.dumps(subcategories)}

    files = {"image": (file_name, image_path, get_mime_type(file_name))}

    response = requests.post(f"{CLASSIFICATION_URI}/fit_categories",
                        files=files,
                        data=categories,
                        headers=header)
    
    return response.json()

@app.task
def get_faceid(client_id):

    header = {"access_token": PG_API_KEY}

    response = requests.post(f"{PG_URI}/get_faceid?id_client={client_id}",
                             headers=header)
    
    return response

def get_mime_type(filename):
    mime_type, encoding = mimetypes.guess_type(filename)
    return mime_type