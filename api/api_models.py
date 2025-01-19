from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    Security, 
    File, 
    UploadFile, 
    Form
)
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey, APIKeyHeader
from models.object_detection import object_detection_model
from models.face_detection import face_detection_model
from models.segmentation import segmentation_model
from models.classification import classification_model
from logger.logging_config import setup_logging
from api.prometheus_metrics import PrometheusMetrics
from utils import utils_image
import os
import json

PREFIX = os.getenv("MODELS_API_ENDPOINT")
API_KEY = os.getenv("MODELS_API_KEY")
TEMP_DIR = os.getenv("IMAGE_TMP_DIR")

logger = setup_logging(__name__)


# Model Instantiation
logger.info("Loading Object Detection Model")
try:
    object_detection = object_detection_model.ObjectDetection(
        model_name=os.getenv("OBJ_DETECTION_MODEL_NAME"),
        temp_dir=TEMP_DIR)
except Exception as e:
    logger.error(f"Error loading object detection model: {e}")
    raise

logger.info("Loading Face Detection Model")
try:
    face_recognition = face_detection_model.FaceDetectionModel(temp_dir=TEMP_DIR)
except Exception as e:
    logger.error(f"Error loading face detection model: {e}")
    raise

logger.info("Loading Segmentation Model")
try:
    segmentation = segmentation_model.SegmentationModel(
        model_name=os.getenv("SEGMENTATION_MODEL_NAME"),
        temp_dir=TEMP_DIR,
        valid_labels=[4, 5, 6, 7])
except Exception as e:
    logger.error(f"Error loading segmentation model: {e}")
    raise

logger.info("Loading Classification Model")
try:
    classification = classification_model.ClassificationModel(
        os.getenv("CLASSIFICATION_MODEL_NAME"))
except Exception as e:
    logger.error(f"Error loading classification model: {e}")
    raise

# API Instatiation
app = FastAPI()
metrics = PrometheusMetrics()
metrics.setup(app)

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Retrieves the API key from the request headers.

    Args:
    api_key_header (str): The API Key from the request headers.

    Returns:
    str: The API Key if it matches the expected value.

    Raises:
    HTTPException: If the API Key does not match the expected value.
    """
    if api_key_header == API_KEY:
        return api_key_header
    else:
        logger.error(f"Could not validate API KEY")
        raise HTTPException(
            status_code=403, 
            detail="Could not validate API KEY"
        )

@app.get("/")
async def root() -> dict:
    """
    Root endpoint that returns a simple message to indicate whether the API is alive.

    This endpoint is useful for checking the health of the API. It does not require any authentication.

    Returns:
    dict: A dictionary with a single key-value pair. The key is "message" and the value is "I'm alive!".
    """
    logger.info("Models API its alive")
    return {"message": "I'm alive!"}

@app.post(f"/{PREFIX}/object_detection")
async def crop_object_image(image: UploadFile = File(...),
                      category_to_detect: str = Form(...),
                      api_key: APIKey = Depends(get_api_key)):
    """
    Perform object detection on the given image and detect the given object type.

    Args:
        image (UploadFile): The image to detect the object in.
        category_to_detect (str): The type of object to detect.

    Returns:
        dict: A dictionary with a single key-value pair. The key is "images" and
            the value is a list of base64 encoded images with the detected object
            cropped out.
    """
    # Convert the image file to a base64 encoded string
    image_base64 = await utils_image.convert_image_to_base64(image)

    try:
        # Perform the object detection
        returned_images = object_detection.detection(
            image_base64,
            category_to_detect)
    except Exception as e:
        # Log the error if the object detection fails
        logger.error(f"Error executing object detection model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong, please contact the administrator."
        )

    # If no images were detected, return a 204 response
    if returned_images == {"images": []}:
        raise HTTPException(
            status_code=204,
            detail=f"Could find any {category_to_detect} in the image"
        )

    return returned_images

@app.post(f"/{PREFIX}/face_detection")
async def face_detection(image: UploadFile = File(...),
                   images_to_search: UploadFile = File(...),
                   api_key: APIKey = Depends(get_api_key)):
    """
    Perform face detection on the given image and detect the given object type.

    Args:
        image (UploadFile): The image to detect the object in.
        images_to_search (UploadFile): The images to search in.

    Returns:
        dict: A dictionary with a single key-value pair. The key is "images" and
            the value is a list of base64 encoded images with the detected object
            cropped out.
    """
    # Convert the image files to base64 encoded strings
    face_id_base64 = await utils_image.convert_image_to_base64(image)
    unknown_image_b64 = await utils_image.convert_image_to_base64(images_to_search)

    try:
        # Perform the face detection
        returned_images = face_recognition.face_recognition(
            face_id_base64,
            unknown_image_b64)
    except Exception as e:
        # Log the error if the face detection fails
        logger.error(f"Error executing face detection model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong, please contact the administrator."
        )

    # If no images were detected, return a 204 response
    if returned_images == {"images": ''}:
        raise HTTPException(
            status_code=204,
            detail=f"Could not find any relation between those images."
        )

    return JSONResponse(content=returned_images)


@app.post(f"/{PREFIX}/single_clothes_segmentation")
async def single_clothes_segmentation(image: UploadFile = File(...),
                        api_key: APIKey = Depends(get_api_key)):
    """
    Perform single clothes segmentation on the given image.

    Args:
        image (UploadFile): The image to detect the clothes in.

    Returns:
        dict: A dictionary with a single key-value pair. The key is "images" and
            the value is a list of base64 encoded images with the detected clothes
            cropped out.
    """
    try:
        # Convert the image file to a base64 encoded string
        image_base64 = await utils_image.convert_image_to_base64(image)
        # Perform the segmentation
        returned_images = segmentation.crop_clothes(image_base64)
    except Exception as e:
        # Log the error if the segmentation fails
        logger.error(f"Error executing segmentation model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong, please contact the administrator."
        )

    # If no images were detected, return a 204 response
    if returned_images == {"images": []}:
        raise HTTPException(
            status_code=204,
            detail=f"Could found any clothes in the image."
        )

    return returned_images


@app.post(f"/{PREFIX}/clothes_segmentation")
async def clothes_segmentation(image: UploadFile = File(...),
                               api_key: APIKey = Depends(get_api_key)):
    """
    Perform clothes segmentation on the given image.

    Args:
        image (UploadFile): The image to perform segmentation on.
        api_key (APIKey): The API key for authentication.

    Returns:
        dict: A dictionary with a single key-value pair. The key is "images" and
            the value is a list of base64 encoded images with the detected clothes
            cropped out.

    Raises:
        HTTPException: If an error occurs during segmentation or if no clothes are found.
    """
    try:
        # Convert the image file to a base64 encoded string
        image_base64 = await utils_image.convert_image_to_base64(image)
        
        # Perform segmentation to crop clothes from the full-body image
        returned_images = segmentation.crop_clothes_from_fullbody(image_base64)
        
    except Exception as e:
        # Log the error if the segmentation fails
        logger.error(f"Error executing segmentation model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong, please contact the administrator."
        )
        
    # If no images were detected, return a 204 response
    if returned_images == {"images": []}:
        raise HTTPException(
            status_code=204,
            detail=f"Could found any clothes in the image."
        )

    return returned_images

@app.post(f"/{PREFIX}/image_classification")
async def get_categories_from_image(
        categories_dict: str = Form(...),
        image: UploadFile = File(...),
        api_key: APIKey = Depends(get_api_key)):
    """
    Perform image classification on the given image and return the categories 
    that best match the image.

    Args:
        categories_dict (str): A JSON string containing the categories to match.
        image (UploadFile): The image to classify.
        api_key (APIKey): The API key for authentication.

    Returns:
        dict: A dictionary with the categories that best match the image.

    Raises:
        HTTPException: If an error occurs during classification or if no categories
            are found.
    """
    try:
        categories_dict = json.loads(categories_dict)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid JSON format for dict_of_categories")

    try:
        image_base64 = await utils_image.convert_image_to_base64(image)
        category = classification.image_classification_from_dict(
            categories_dict,
            image_base64)
    except Exception as e:
        logger.error(f"Error executing classification model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong, please contact the administrator."
        )
        
    if category == {}:
        raise HTTPException(
            status_code=204, 
            detail="Could not identify any category for this image.")
    
    return category
