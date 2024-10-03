from fastapi import Depends, FastAPI, HTTPException
from classification import classification_model
from schemas import schema
import yaml
import uvicorn
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
    return config['webservice_categorization'], config['classification_model']

# Load database configuration from the YAML file
ws_config, model_config = load_config()

PREFIX = ws_config['prefix']
MODEL = model_config['model_name']

app = FastAPI()

classification = classification_model.ClassificationModel(MODEL)

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}

@app.get(f"/{PREFIX}/fit_category", response_model=str)
def get_category_from_image(image_to_classify: schema.ImageClassification):
    category = classification.image_classification_from_list(image_to_classify)
    return category

@app.get(f"/{PREFIX}/fit_categories", response_model=dict)
def get_categories_from_image(image_to_classify: schema.ImageClassificationDict):
    category = classification.image_classification_from_dict(image_to_classify)
    return category

# if __name__ == "__main__":
#     uvicorn.run(app_categorization, host="0.0.0.0", port=PORT)