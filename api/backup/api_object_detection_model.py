from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    Security, 
    File, 
    UploadFile, 
    Response, 
    Form
)
from fastapi.security.api_key import APIKey, APIKeyHeader
from models.object_detection import object_detection_model
from pathlib import Path
import shutil
import tempfile
import io
import zipfile
import os
import time
import base64

PREFIX = os.getenv("OBJ_DETECTION_API_ENDPOINT")
API_KEY = os.getenv("OBJ_DETECTION_API_KEY")

MODEL = os.getenv("OBJ_DETECTION_MODEL_NAME")
TEMP_DIR = os.getenv("IMAGE_TMP_DIR")

# Model Instantiation
object_detection = object_detection_model.ObjectDetection(
    model_name=MODEL,
    temp_dir=TEMP_DIR)

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


def zipfiles(filenames):
    timestamp = int(time.time())
    zip_filename = f"identified_objects_{timestamp}.zip"

    s = io.BytesIO()
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)

        # Add file, at correct path
        zf.write(fpath, fname)

    # Must close zip for all contents to be written
    zf.close()

    # Delete images after have been zipped
    for fpath in filenames:
        os.remove(fpath)

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = Response(s.getvalue(),
                    media_type="application/x-zip-compressed",
                    headers={'Content-Disposition': f'attachment;filename={zip_filename}'
                             })

    return resp

async def convert_image_to_base64(image: UploadFile) -> str:
    image_bytes = await image.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    return image_base64

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}


@app.post(f"/{PREFIX}/crop_detection", response_model=list[str])
def crop_object_image(image: UploadFile = File(...),
                      category_to_detect: str = Form(...),
                      api_key: APIKey = Depends(get_api_key)):
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        temp_image_path = temp_dir_path / image.filename

        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

            returned_images = object_detection.detection(
                str(temp_image_path),
                category_to_detect)

        if returned_images == []:
            raise HTTPException(
                status_code=204,
                detail=f"Could find any {category_to_detect} in the image"
            )

    return zipfiles(returned_images)

@app.post(f"/{PREFIX}/crop_detection_new")
async def crop_object_image_new(image: UploadFile = File(...),
                      category_to_detect: str = Form(...),
                      api_key: APIKey = Depends(get_api_key)):
    
    image_base64 = await convert_image_to_base64(image)

    returned_images = object_detection.detection_new(
        image_base64,
        category_to_detect)

    if returned_images == {"images": []}:
        raise HTTPException(
            status_code=204,
            detail=f"Could find any {category_to_detect} in the image"
        )

    return returned_images
