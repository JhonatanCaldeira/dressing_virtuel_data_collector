from fastapi import Depends, FastAPI, HTTPException, Security, Form, File, UploadFile
from fastapi.security.api_key import APIKey, APIKeyHeader
from models.classification import classification_model
import os
import json
import tempfile
from pathlib import Path
import shutil

PREFIX = os.getenv("CLASSIFICATION_API_ENDPOINT")
API_KEY = os.getenv("CLASSIFICATION_API_KEY")
MODEL = os.getenv("CLASSIFICATION_MODEL_NAME")

# Model Instantiation
classification = classification_model.ClassificationModel(MODEL)

app = FastAPI()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate API KEY"
        )


@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}


@app.post(f"/{PREFIX}/fit_categories", response_model=dict)
def get_categories_from_image(
        categories_dict: str = Form(...),
        image: UploadFile = File(...),
        api_key: APIKey = Depends(get_api_key)):

    try:
        categories_dict = json.loads(categories_dict)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid JSON format for dict_of_categories")

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        temp_image_path = temp_dir_path / image.filename

        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

            category = classification.image_classification_from_dict(
                categories_dict,
                str(temp_image_path))
        

    if category == {}:
        raise HTTPException(
            status_code=204, 
            detail="Could not identify any category for this image.")
    
    return category
