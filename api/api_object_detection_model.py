from fastapi import Depends, FastAPI, HTTPException, Security, File, UploadFile, Response, Form
from fastapi.security.api_key import APIKey, APIKeyHeader
from fastapi.responses import FileResponse
from starlette.status import HTTP_403_FORBIDDEN
from object_detection import object_detection_model
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
    return config['webservice_detection'], config['object_detection_model']

# Load database configuration from the YAML file
ws_config, model_config = load_config()

PREFIX = ws_config['prefix']
API_KEY = ws_config['API_KEY'] #REVOIR APRES

MODEL = model_config['model_name']
TEMP_DIR = model_config['image_temporary_directory']

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
        
    return zipfiles(returned_images)