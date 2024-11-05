from celery import Celery
from PIL import Image
from utils import utils_image
import requests
import json
import io, zipfile
import os
import time
import base64


from dotenv import load_dotenv
load_dotenv(dotenv_path="config/.env")

# Define the path where the fashion dataset is stored
IMAGE_TMP_DIR = os.getenv("IMAGE_TMP_DIR")
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

    face_id_b64 = get_faceid(id_client)
    face_id_byte_arr = utils_image.image_base64_to_buffer(face_id_b64)

    for image_path in image_paths:
        obj_response = object_detection(image_path,'person')

        if obj_response.status_code != 200:
            continue

        data_obj_detection = json.loads(obj_response.content)
        for image_base64 in data_obj_detection['images']:
            obj_detec_byte_arr = utils_image.image_base64_to_buffer(image_base64)

            face_response = face_detection(face_id_byte_arr, 
                                        obj_detec_byte_arr)

            if face_response.status_code == 200:
                data_face_detection = json.loads(face_response.content)
                break
        
        face_detection_buffer = utils_image.image_base64_to_buffer(
            data_face_detection['images'])

        segment_response = image_segmentation(face_detection_buffer)
        if segment_response.status_code == 200:
            data_segmentation = json.loads(segment_response.content)

            for img_segmentation in data_segmentation['images']:
                img_seg_buffer = utils_image.image_base64_to_buffer(img_segmentation)
                image_classification(dict_of_categories, 
                                     img_seg_buffer, 
                                     utils_image.generate_image_name())

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
def face_detection(image, images_to_search):

    image_file = open(image, "rb")
    images_to_search_file = open(images_to_search, "rb") 
    files = {"image": (image, 
                        image_file, 
                        utils_image.get_mime_type(image)),
            "images_to_search" : (images_to_search, 
                                    images_to_search_file,
                                    utils_image.get_mime_type(
                                        images_to_search))}

    response = requests.post(f"{MODELS_URI}/face_detection",
                        files=files,
                        headers=HEADER)
    
    image_file.close()
    images_to_search_file.close()
    
    return response

@app.task
def image_segmentation(image_path):
    with open(image_path, "rb") as image_file:
        files = {"image": (image_path, 
                           image_file, 
                           utils_image.get_mime_type(image_path))}
        
        response = requests.post(f"{MODELS_URI}/clothes_segmentation",
                                files=files,
                                headers=HEADER)

    return response

@app.task
def image_classification(subcategories, image_path, file_name):
    categories = {'categories_dict': json.dumps(subcategories)}

    files = {"image": (file_name, 
                       image_path, 
                       utils_image.get_mime_type(file_name))}

    response = requests.post(f"{MODELS_URI}/image_classification",
                        files=files,
                        data=categories,
                        headers=HEADER)
    
    return response.json()

@app.task
def get_faceid(client_id):

    header = {"access_token": PG_API_KEY}
    response = requests.post(f"{PG_URI}/get_faceid?id_client={client_id}",
                             headers=header)
    
    return response