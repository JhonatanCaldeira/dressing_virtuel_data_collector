from fastapi import Depends, FastAPI, HTTPException, Security, Form, File, UploadFile,Body
from fastapi.security.api_key import APIKey, APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from typing import Annotated
from classification import classification_model
from schemas import schema
import yaml
import json
import tempfile
from pathlib import Path
import shutil

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
    return config['webservice_categorization'], config['classification_model']

# Load database configuration from the YAML file
ws_config, model_config = load_config()

PREFIX = ws_config['prefix']
API_KEY = ws_config['API_KEY'] #REVOIR APRES

MODEL = model_config['model_name']

# Model Instantiation
classification = classification_model.ClassificationModel(MODEL)

app = FastAPI()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header   
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
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
        raise HTTPException(status_code=400, detail="Invalid JSON format for dict_of_categories")

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        temp_image_path = temp_dir_path / image.filename

        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        category = classification.image_classification_from_dict(
                                                categories_dict,
                                                str(temp_image_path))
    return category

# if __name__ == "__main__":
#     uvicorn.run(app_categorization, host="0.0.0.0", port=PORT)