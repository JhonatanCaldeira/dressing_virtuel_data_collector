import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image  # Import Image from PIL
import requests
import json
import open_clip
import torch
import os

# Define the path where the fashion dataset is stored
FASHION_DATASET_HOME = '/home/jcaldeira/dressing_virtuel_data_collector/image_scraper/images/full'

# API endpoint to send requests
ENDPOINT = 'http://127.0.0.1:5000/dressing_virtuel'
ENDPOINT_CATE = 'http://127.0.0.1:5001/categorization_model'


def get_categories(method, key):
    """
    Fetches categories (like gender, color, season, etc.) from the API.

    Args:
        method (str): API method to fetch (e.g., 'genders', 'colors').
        key (str): The key to extract from the API response (e.g., 'name', 'id').

    Returns:
        dict: A dictionary with category names as keys and their 
        corresponding IDs as values.
    """
    response = requests.get(f"{ENDPOINT}/{method}")
    dict = {x[key]: x['id'] for x in response.json()}

    return dict

def clip_evaluation(subcategories, image_path):
    json_post_image = {"path": image_path, "list_of_categories": subcategories}
    response = requests.get(f"{ENDPOINT_CATE}/fit_category",data = json.dumps(json_post_image))
    return response.json()

# Fetch categories from the API and store them in dictionaries
dict_genders = get_categories('genders','gender')
dict_seasons = get_categories('seasons','name')
dict_colors = get_categories('colors','name')
dict_usage = get_categories('usage_types','name')
dict_article = get_categories('article_types','name')

# Loop through all images in the dataset
for image in os.listdir(FASHION_DATASET_HOME):
    image_path = FASHION_DATASET_HOME + '/' + image

    # Perform CLIP evaluation to get the best matching category for each attribute
    gender = clip_evaluation(list(dict_genders.keys()),image_path)
    season = clip_evaluation(list(dict_seasons.keys()),image_path)
    color = clip_evaluation(list(dict_colors.keys()),image_path)
    usage = clip_evaluation(list(dict_usage.keys()),image_path)
    article = clip_evaluation(list(dict_article.keys()),image_path)

    # Create a JSON object to send to the API
    json_post_image = {"id":0,
                       "path":image_path, 
                       "id_usagetype":usage,
                       "id_gender":gender,
                       "id_color":color,
                       "id_season":season,
                       "id_articletype":article}

    print(json_post_image)
    # Send the image metadata to the API for import
    #response = requests.post(f"{ENDPOINT}/import_image", data = json.dumps(json_post_image))



    # Check the response status
    # if response.status_code == 200:
    #     print(response.text)  # Access the response data (usually JSON)
    # else:
    #     print(f"Error: {response.status_code}")