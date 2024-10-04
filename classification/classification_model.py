from PIL import Image  # Import Image from PIL
from schemas import schema
import open_clip
import torch

class ClassificationModel():

    def __init__(self, model_name: str):
        (self.model, 
         self.preprocess_train, 
         self.preprocess_val, 
         self.tokenizer, 
         self.device) = self.load_model(model_name)

    def load_model(self, model_name: str):
        #Load the Marqo/marqo-fashionCLIP model and preprocessors
        (model, 
         preprocess_train, 
         preprocess_val) = open_clip.create_model_and_transforms(model_name)
        
        tokenizer = open_clip.get_tokenizer(model_name)

        # Set the device (GPU if available, otherwise CPU)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device) # Move the model to the selected device

        return model, preprocess_train, preprocess_val, tokenizer, device

    def image_classification_from_dict(self,
                                       dict_of_categories: dict,
                                       image_to_classify: str):
        """
        Evaluates the similarity between an image and a dict of subcategory 
        descriptions using CLIP.

        Args:
            image_to_classify (schema.ImageClassificationDict): The ImageClassificationDict
            schema object containing image details.

        Returns:
            dict: Dict of subcategories that has the highest similarity score to the image.
        """
        model = self.model
        preprocess_val = self.preprocess_val
        tokenizer = self.tokenizer
        device = self.device

        result_dict = {}
        for key, list_of_cat in dict_of_categories.items():
            # Preprocess the text descriptions for each subcategory using the tokenizer
            text_inputs = tokenizer([f"a photo of {c}" for c in 
                                    list_of_cat]).to(device)

            # Open and preprocess the image
            with open(image_to_classify, 'rb') as path:
                image = Image.open(path)
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

            result_dict[key] = dict_of_categories[key][indices[0]]
                
        return result_dict # Return the best matching subcategory