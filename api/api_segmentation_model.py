from fastapi import Depends, FastAPI, HTTPException
from segformer_clothes_model import segmentation_model
from typing import Annotated
from schemas import schema
import yaml
import uvicorn
import os
import base64

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
    return config['webservice_segmentation']

# Load database configuration from the YAML file
ws_config = load_config()
PREFIX = ws_config['prefix']
# PORT = ws_config['port']

app = FastAPI()

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}

@app.get(f"/{PREFIX}/crop_single_clothes", response_model=list[str])
def crop_single_clothes(image_to_segmentation: schema.ImageSegmentation):
    image = segmentation_model.crop_clothes(image_to_segmentation)
    return image

@app.get(f"/{PREFIX}/crop_fullbody_clothes", response_model=list[str])
def crop_fullbody_clothes(image_to_segmentation: schema.ImageSegmentation):
    images = segmentation_model.crop_clothes_from_fullbody(image_to_segmentation)
    return images

# if __name__ == "__main__":
#     uvicorn.run(app_categorization, host="0.0.0.0", port=PORT)