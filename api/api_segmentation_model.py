from fastapi import Depends, FastAPI, HTTPException, Security, File, UploadFile, Response
from fastapi.security.api_key import APIKey, APIKeyHeader
from fastapi.responses import FileResponse
from starlette.status import HTTP_403_FORBIDDEN
import starlette
from segformer_clothes_model import segmentation_model
from schemas import schema
from pathlib import Path
import yaml
import shutil
import tempfile
import io
import zipfile
import os

def load_config(filepath='config/config.yaml'):
    """
    Loads the webservice configuration from a YAML file.

    Args:
        filepath (str): Path to the YAML configuration file.

    Returns:
        dict: A dictionary containing the database configuration.
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config['webservice_segmentation'], config['segmentation_model']

# Load database configuration from the YAML file
ws_config, model_config = load_config()

PREFIX = ws_config['prefix']
API_KEY = ws_config['API_KEY'] #REVOIR APRES

MODEL = model_config['model_name']
VALID_LABELS = model_config['valid_labels']
TEMP_DIR = model_config['image_temporary_directory']

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
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
    
def zipfiles(filenames):
    zip_filename = "archive.zip"

    s = io.BytesIO()
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)

        # Add file, at correct path
        zf.write(fpath, fname)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = Response(s.getvalue(), 
                    media_type="application/x-zip-compressed", 
                    headers={'Content-Disposition': f'attachment;filename={zip_filename}'
        })

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

    return zipfiles(returned_images)

@app.post(f"/{PREFIX}/crop_fullbody_clothes", response_model=list[str])
def crop_fullbody_clothes(image: UploadFile= File(...),
                        api_key: APIKey = Depends(get_api_key)):
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        temp_image_path = temp_dir_path / image.filename

        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        returned_images = segmentation.crop_clothes_from_fullbody(str(temp_image_path))
        
    return zipfiles(returned_images)

# if __name__ == "__main__":
#     uvicorn.run(app_categorization, host="0.0.0.0", port=PORT)