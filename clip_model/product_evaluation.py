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
    """
    Evaluates the similarity between an image and a list of subcategory 
    descriptions using CLIP.

    Args:
        subcategories (list): List of subcategory names.
        image_path (str): Path to the image file.

    Returns:
        str: The subcategory that has the highest similarity score to the image.
    """
   
    # Preprocess the text descriptions for each subcategory using the tokenizer
    text_inputs = tokenizer([f"a photo of {c}" for c in subcategories]).to(device)

    # Open and preprocess the image
    image = Image.open(image_path)
    image_input = preprocess_val(image).unsqueeze(0).to(device)

    # Calculate image and text features
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_inputs)

    # Normalize the features
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # Calculate similarity between image and text features
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    values, indices = similarity[0].topk(1) # Get the top 1 matching subcategory

    image.close() # Close the image after processing

    return subcategories[indices[0]] # Return the best matching subcategory

print("Loading Model")
#Load the Marqo/marqo-fashionCLIP model and preprocessors
model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms('hf-hub:Marqo/marqo-fashionSigLIP')
tokenizer = open_clip.get_tokenizer('hf-hub:Marqo/marqo-fashionSigLIP')

# Set the device (GPU if available, otherwise CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device) # Move the model to the selected device

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
                       "id_usagetype":dict_usage[usage],
                       "id_gender":dict_genders[gender],
                       "id_color":dict_colors[color],
                       "id_season":dict_seasons[season],
                       "id_articletype":dict_article[article]}

    # Send the image metadata to the API for import
    response = requests.post(f"{ENDPOINT}/import_image", data = json.dumps(json_post_image))

    # Check the response status
    if response.status_code == 200:
        print(response.text)  # Access the response data (usually JSON)
    else:
        print(f"Error: {response.status_code}")