from fastapi import Depends, FastAPI, HTTPException, Security, File, UploadFile, Response
from fastapi.security.api_key import APIKey, APIKeyHeader
from models.segmentation import segmentation_model
from pathlib import Path
import shutil
import tempfile
import io
import zipfile
import os
import time

PREFIX = os.getenv("SEGMENTATION_API_ENDPOINT")
API_KEY = os.getenv("SEGMENTATION_API_KEY")

MODEL = os.getenv("SEGMENTATION_MODEL_NAME")
VALID_LABELS = [4, 5, 6, 7]
TEMP_DIR = os.getenv("IMAGE_TMP_DIR")

# Model Instantiation
segmentation = segmentation_model.SegmentationModel(
    model_name=MODEL,
    temp_dir=TEMP_DIR,
    valid_labels=VALID_LABELS)

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
    zip_filename = f"segmented_clothes_{timestamp}.zip"

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
                    headers={'Content-Disposition': f'attachment;filename={zip_filename}'})

    return resp


@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}


@app.post(f"/{PREFIX}/crop_single_clothes")
def crop_single_clothes(image: UploadFile = File(...),
                        api_key: APIKey = Depends(get_api_key)):

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        # Define the file path in the temporary directory
        temp_image_path = temp_dir_path / image.filename

        # Save the uploaded file to the temporary directory
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        returned_images = segmentation.crop_clothes(str(temp_image_path))

    if returned_images == []:
        raise HTTPException(
            status_code=204,
            detail=f"Could found any clothes in the image.")

    return zipfiles(returned_images)


@app.post(f"/{PREFIX}/crop_fullbody_clothes", response_model=list[str])
def crop_fullbody_clothes(image: UploadFile = File(...),
                          api_key: APIKey = Depends(get_api_key)):

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        temp_image_path = temp_dir_path / image.filename

        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        returned_images = segmentation.crop_clothes_from_fullbody(
            str(temp_image_path))
        
    if returned_images == []:
        raise HTTPException(
            status_code=204,
            detail=f"Could found any clothes in the image.")

    return zipfiles(returned_images)