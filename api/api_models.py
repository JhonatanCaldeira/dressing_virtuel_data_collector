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
from utils import utils_image
import os
import json

PREFIX = os.getenv("MODELS_API_ENDPOINT")
API_KEY = os.getenv("MODELS_API_KEY")
TEMP_DIR = os.getenv("IMAGE_TMP_DIR")

# Model Instantiation
print("Loading Object Detection Model")
object_detection = object_detection_model.ObjectDetection(
    model_name=os.getenv("OBJ_DETECTION_MODEL_NAME"),
    temp_dir=TEMP_DIR)

print("Loading Face Detection Model")
face_recognition = face_detection_model.FaceDetectionModel(temp_dir=TEMP_DIR)

print("Loading Segmentation Model")
VALID_LABELS = [4, 5, 6, 7]
segmentation = segmentation_model.SegmentationModel(
    model_name=os.getenv("SEGMENTATION_MODEL_NAME"),
    temp_dir=TEMP_DIR,
    valid_labels=VALID_LABELS)

print("Loading Classification Model")
classification = classification_model.ClassificationModel(
    os.getenv("CLASSIFICATION_MODEL_NAME"))

# API Instatiation
app = FastAPI()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, 
            detail="Could not validate API KEY"
        )

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}

@app.post(f"/{PREFIX}/object_detection")
async def crop_object_image(image: UploadFile = File(...),
                      category_to_detect: str = Form(...),
                      api_key: APIKey = Depends(get_api_key)):
    
    image_base64 = await utils_image.convert_image_to_base64(image)

    returned_images = object_detection.detection(
        image_base64,
        category_to_detect)

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

    face_id_base64 = await utils_image.convert_image_to_base64(image)
    unknown_image_b64 = await utils_image.convert_image_to_base64(images_to_search)

    returned_images = face_recognition.face_recognition(
        face_id_base64,
        unknown_image_b64)

    if returned_images == {"images": ''}:
        raise HTTPException(
            status_code=204,
            detail=f"Could not find any relation between those images."
        )

    return JSONResponse(content=returned_images)


@app.post(f"/{PREFIX}/single_clothes_segmentation")
async def single_clothes_segmentation(image: UploadFile = File(...),
                        api_key: APIKey = Depends(get_api_key)):

    image_base64 = await utils_image.convert_image_to_base64(image)
    returned_images = segmentation.crop_clothes(image_base64)

    if returned_images == {"images": []}:
        raise HTTPException(
            status_code=204,
            detail=f"Could found any clothes in the image.")

    return returned_images


@app.post(f"/{PREFIX}/clothes_segmentation")
async def clothes_segmentation(image: UploadFile = File(...),
                          api_key: APIKey = Depends(get_api_key)):

    image_base64 =  await utils_image.convert_image_to_base64(image)
    returned_images = segmentation.crop_clothes_from_fullbody(image_base64)
        
    if returned_images == {"images": []}:
        raise HTTPException(
            status_code=204,
            detail=f"Could found any clothes in the image.")

    return returned_images

@app.post(f"/{PREFIX}/image_classification")
async def get_categories_from_image(
        categories_dict: str = Form(...),
        image: UploadFile = File(...),
        api_key: APIKey = Depends(get_api_key)):

    try:
        categories_dict = json.loads(categories_dict)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid JSON format for dict_of_categories")

    image_base64 = await utils_image.convert_image_to_base64(image)
    category = classification.image_classification_from_dict(
        categories_dict,
        image_base64)
        
    if category == {}:
        raise HTTPException(
            status_code=204, 
            detail="Could not identify any category for this image.")
    
    return category
