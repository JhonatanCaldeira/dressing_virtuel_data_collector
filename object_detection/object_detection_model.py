from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
from schemas import schema
import torch
import time
import random
import string
import os

class ObjectDetection:

    def __init__(self, model_name: str, temp_dir: str):
        (
            self.processor,
            self.model,
            self.device
        ) = self.load_model(model_name)
        self.set_image_temporary_directory(temp_dir)

    def load_model(self, model_name: str):
        # you can specify the revision tag if you don't want the timm dependency
        processor = DetrImageProcessor.from_pretrained(model_name, revision="no_timm")
        model = DetrForObjectDetection.from_pretrained(model_name, revision="no_timm")

        # Set the device to GPU if available, otherwise use CPU
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)  # Move the model to the selected device

        return processor, model, device
    
    def set_image_temporary_directory(self, temp_dir):
        self.__temp_dir = temp_dir

    def generate_image_name(self, extension="png"):
        # Get the current timestamp
        timestamp = int(time.time())
        
        # Generate a random string of 6 characters
        random_str = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=6))
        
        # Combine timestamp and random string to create the image name
        image_name = f"image_{timestamp}_{random_str}.{extension}"
        
        return image_name
    
    def detection(self, image_path: str, category_to_detect: str):
        processor = self.processor
        model = self.model
        device = self.device

        with open(image_path, 'rb') as path:
            image = Image.open(path)

            inputs = processor(images=image, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            outputs = model(**inputs)

            # convert outputs (bounding boxes and class logits) to COCO API
            # let's only keep detections with score > 0.9
            target_sizes = torch.tensor([image.size[::-1]])
            results = processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=0.9)[0]

            return_images = []
            for label, box in zip(results["labels"], results["boxes"]):
                if model.config.id2label[label.item()] != category_to_detect:
                    continue
                box = [round(i, 2) for i in box.tolist()]

                cropped_image = image.crop(box)
                cropped_image_path = os.path.join(self.__temp_dir, 
                                        self.generate_image_name())
                cropped_image.save(cropped_image_path)
                return_images.append(cropped_image_path)

        return return_images