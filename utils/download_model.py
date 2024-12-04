from transformers import DetrForObjectDetection, DetrImageProcessor
from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
import os

def download_obj_detection_model(model_path, model_name):
    """Download a Hugging Face model and tokenizer to the specified directory"""
    # Check if the directory already exists
    if not os.path.exists(model_path):
        # Create the directory
        os.makedirs(model_path)

    processor = DetrImageProcessor.from_pretrained(model_name)
    model = DetrForObjectDetection.from_pretrained(model_name)

    # Save the model and tokenizer to the specified directory
    model.save_pretrained(model_path)
    processor.save_pretrained(model_path)

def download_segmentation_model(model_path, model_name):
    """Download a Hugging Face model and tokenizer to the specified directory"""
    # Check if the directory already exists
    if not os.path.exists(model_path):
        # Create the directory
        os.makedirs(model_path)

    processor = SegformerImageProcessor.from_pretrained(model_name)
    model = AutoModelForSemanticSegmentation.from_pretrained(model_name)
    
    # Save the model and tokenizer to the specified directory
    model.save_pretrained(model_path)
    processor.save_pretrained(model_path)

OBJ_DETECTION_MODEL_NAME = os.getenv("OBJ_DETECTION_MODEL_NAME")
OBJ_DETECTION_MODEL_DIR = os.getenv("OBJ_DETECTION_MODEL_DIR")

download_obj_detection_model(OBJ_DETECTION_MODEL_DIR, OBJ_DETECTION_MODEL_NAME)

SEGMENTATION_MODEL_NAME = os.getenv("SEGMENTATION_MODEL_NAME")
SEGMENTATION_MODEL_DIR = os.getenv("SEGMENTATION_MODEL_DIR")

download_segmentation_model(OBJ_DETECTION_MODEL_DIR, OBJ_DETECTION_MODEL_NAME)
