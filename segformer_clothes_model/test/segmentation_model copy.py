from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from schemas import schema
from PIL import Image
import torch.nn as nn
import torch
import numpy as np
import base64
import io
import time
import random
import string
import os

MODEL = "sayeed99/segformer_b3_clothes"
TMP_DIRECOTY = '/home/jcaldeira/dressing_virtuel_data_collector/media/tmp/'
VALID_LABELS = [4, 5, 6, 7]
"""
# Class ID: 0, Class Name: Background
# Class ID: 1, Class Name: Hat
# Class ID: 2, Class Name: Hair
# Class ID: 3, Class Name: Sunglasses
# Class ID: 4, Class Name: Upper-clothes
# Class ID: 5, Class Name: Skirt
# Class ID: 6, Class Name: Pants
# Class ID: 7, Class Name: Dress
# Class ID: 8, Class Name: Belt
# Class ID: 9, Class Name: Left-shoe
# Class ID: 10, Class Name: Right-shoe
# Class ID: 11, Class Name: Face
# Class ID: 12, Class Name: Left-leg
# Class ID: 13, Class Name: Right-leg
# Class ID: 14, Class Name: Left-arm
# Class ID: 15, Class Name: Right-arm
# Class ID: 16, Class Name: Bag
# Class ID: 17, Class Name: Scarf
# """

def generate_image_name(extension="png"):
    # Get the current timestamp
    timestamp = int(time.time())
    
    # Generate a random string of 6 characters
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # Combine timestamp and random string to create the image name
    image_name = f"image_{timestamp}_{random_str}.{extension}"
    
    return image_name

def clothes_segmentation(image_path):
    """
    Segments clothing from a given image using a pre-trained semantic segmentation model.

    Args:
        image_path (str): The file path to the image that will be segmented.

    Returns:
        Tuple[torch.Tensor, AutoModelForSemanticSegmentation]: 
            - upsampled_logits (torch.Tensor): The logits after upsampling to the original image size.
    """
    
    # Load the image processor and the pre-trained model for semantic segmentation
    processor = SegformerImageProcessor.from_pretrained(MODEL)
    model = AutoModelForSemanticSegmentation.from_pretrained(MODEL)

    # Set the device to GPU if available, otherwise use CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)  # Move the model to the selected device

    # Open and preprocess the image for the model
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")

    # Move inputs to the same device as the model
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Perform inference to obtain logits from the model
    outputs = model(**inputs)
    logits = outputs.logits

    # Upsample the logits to match the original image size
    upsampled_logits = nn.functional.interpolate(
        logits,
        size=image.size[::-1],  # Reverse the size to (height, width)
        mode="bilinear",
        align_corners=False,
    )

    # Close the opened image file to free resources
    image.close()

    return upsampled_logits

def crop_clothes_from_fullbody(image_to_segment: schema.ImageSegmentation):
    """
    Segments clothing from a full-body image and crops out the 
    detected clothing items.

    Args:
        image_to_segment (str): The file path to the full-body 
        image that will be segmented.

    Returns:
        List[str]: Return a list of paths to the temporary images.
    """
    
    # Set the device to GPU if available, otherwise use CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Perform segmentation on the input image, returning logits 
    upsampled_logits = clothes_segmentation(image_to_segment.path)
    upsampled_logits = upsampled_logits.to(device)

    # Obtain the segmentation map by applying argmax to the logits
    pred_seg = upsampled_logits.argmax(dim=1)[0].cpu().numpy()

    # Apply Softmax to normalize probabilities for each class
    probabilities = nn.functional.softmax(upsampled_logits, dim=1)  

    # Create a certainty mask for probabilities exceeding 70%
    certainty_mask = (probabilities.max(dim=1).values > 0.7).to(device)  
    certainty_mask_np = certainty_mask.squeeze().cpu().numpy()

    # Filter unique labels in the segmentation map, only where certainty is > 70%
    unique_labels = np.unique(pred_seg[certainty_mask_np]) 

    # Open the original image
    return_images = []
    with open(image_to_segment.path, 'rb') as path:
        image = Image.open(path)    

        for label in unique_labels:
            # Skip labels that are not in the valid_labels list
            if label not in VALID_LABELS:
                continue
            
            # Convert the segmentation map to a binary mask for the target class
            target_class = label  # Define the class to be extracted
            binary_mask = (pred_seg == target_class).astype(np.uint8)

            # Find the bounding box of the target segment using non-zero indices of the binary mask
            non_zero_indices = np.nonzero(binary_mask)
            
            # Calculate the bounding box limits (min and max coordinates)
            min_y, max_y = np.min(non_zero_indices[0]), np.max(non_zero_indices[0])
            min_x, max_x = np.min(non_zero_indices[1]), np.max(non_zero_indices[1])

            # Crop the original image using the calculated bounding box limits
            cropped_image = image.crop((min_x, min_y, max_x, max_y))
            cropped_image_path = os.path.join(TMP_DIRECOTY, 
                                            generate_image_name())
            
            cropped_image.save(cropped_image_path)
            return_images.append(cropped_image_path)

    return return_images 

def crop_clothes(image_to_segment: schema.ImageSegmentation):
    """
    Segments clothing from a single clothe image and crops out the 
    detected clothing.

    Args:
        image_to_segment (str): The file path to the full-body 
        image that will be segmented.

    Returns:
        List[str]: Return a list of paths to the temporary images.
    """
    upsampled_logits = clothes_segmentation(image_to_segment.path)

    # Get the segmentation map
    pred_seg = upsampled_logits.argmax(dim=1)[0].cpu().numpy()

    # Get unique class labels present in the predicted segmentation map
    unique_labels, counts = np.unique(pred_seg, return_counts=True)

    # Create a dictionary to store label counts excluding label 0 (Background)
    label_counts = {label: count for label, count in 
                    zip(unique_labels, counts) if label != 0}

    # Get the label with the most values
    max_label = max(label_counts, key=label_counts.get)

    # Convert the segmentation map to a binary mask 
    target_class = max_label
    binary_mask = (pred_seg == target_class).astype(np.uint8)

    with open(image_to_segment.path, 'rb') as path:
        # Create a blank (transparent) image with the same size as the original image
        image = Image.open(path)
        cropped_image = Image.new("RGBA", image.size)

        # Apply the mask to the original image
        cropped_image = Image.composite(image.convert("RGBA"), 
                                        cropped_image, 
                                        Image.fromarray(binary_mask * 255))

        # Crop the image to remove excess transparent borders
        non_zero_indices = np.nonzero(binary_mask)
        min_y, max_y = np.min(non_zero_indices[0]), np.max(non_zero_indices[0])
        min_x, max_x = np.min(non_zero_indices[1]), np.max(non_zero_indices[1])
        cropped_image = cropped_image.crop((min_x, min_y, max_x, max_y))

        cropped_image_path = os.path.join(TMP_DIRECOTY, 
                                        generate_image_name())
        cropped_image.save(cropped_image_path)

    return_images = []
    return_images.append(cropped_image_path)

    return return_images

if __name__ == "__main__":
    clothes_segmentation('segformer_clothes_model/images/100_0519.JPG')