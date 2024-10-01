from PIL import Image  # Import Image from PIL
from schemas import schema
import open_clip
import torch

def clip_evaluation(image_to_classify: schema.ImageClassification):
    """
    Evaluates the similarity between an image and a list of subcategory 
    descriptions using CLIP.

    Args:
        image_to_classify (schema.ImageClassification): The ImageClassification
          schema object containing image details.


    Returns:
        str: The subcategory that has the highest similarity score to the image.
    """
   
    print("Loading Model")
    #Load the Marqo/marqo-fashionCLIP model and preprocessors
    model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms(
        'hf-hub:Marqo/marqo-fashionSigLIP')
    tokenizer = open_clip.get_tokenizer('hf-hub:Marqo/marqo-fashionSigLIP')

    # Set the device (GPU if available, otherwise CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device) # Move the model to the selected device

    # Preprocess the text descriptions for each subcategory using the tokenizer
    text_inputs = tokenizer([f"a photo of {c}" for c in image_to_classify.list_of_categories]).to(device)

    # Open and preprocess the image
    image = Image.open(image_to_classify.path)
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

    return image_to_classify.list_of_categories[indices[0]] # Return the best matching subcategory