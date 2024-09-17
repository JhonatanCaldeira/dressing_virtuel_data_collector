import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image  # Import Image from PIL
import requests
import json
import open_clip
import torch
import os

FASHION_DATASET_HOME = '/home/jcaldeira/dressing_virtuel_data_collector/image_scraper/images/full'
ENDPOINT = 'http://127.0.0.1:5000/dressing_virtuel'

def get_categories(method, key):
    response = requests.get(f"{ENDPOINT}/{method}")
    dict = {x[key]: x['id'] for x in response.json()}

    return dict

def clip_evaluation(subcategories, image_path):
    # Preprocess the text descriptions for each subcategory using the tokenizer
    text_inputs = tokenizer([f"a photo of {c}" for c in subcategories]).to(device)

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
    values, indices = similarity[0].topk(1)

    image.close()

    return subcategories[indices[0]]

print("Loading Model")
#Load the Marqo/marqo-fashionCLIP model and preprocessors
model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms('hf-hub:Marqo/marqo-fashionSigLIP')
tokenizer = open_clip.get_tokenizer('hf-hub:Marqo/marqo-fashionSigLIP')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

dict_genders = get_categories('genders','gender')
dict_seasons = get_categories('seasons','name')
dict_colors = get_categories('colors','name')
dict_usage = get_categories('usage_types','name')
dict_article = get_categories('article_types','name')

for image in os.listdir(FASHION_DATASET_HOME):
    image_path = FASHION_DATASET_HOME + '/' + image

    gender = clip_evaluation(list(dict_genders.keys()),image_path)
    season = clip_evaluation(list(dict_seasons.keys()),image_path)
    color = clip_evaluation(list(dict_colors.keys()),image_path)
    usage = clip_evaluation(list(dict_usage.keys()),image_path)
    article = clip_evaluation(list(dict_article.keys()),image_path)

    json_post_image = {"id":0,
                       "path":image_path, 
                       "id_usagetype":dict_usage[usage],
                       "id_gender":dict_genders[gender],
                       "id_color":dict_colors[color],
                       "id_season":dict_seasons[season],
                       "id_articletype":dict_article[article]}
    #print(json_post_image)
    response = requests.post(f"{ENDPOINT}/import_image", data = json.dumps(json_post_image))

    if response.status_code == 200:
        print(response.text)  # Access the response data (usually JSON)
    else:
        print(f"Error: {response.status_code}")