from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import torch
import os
import base64
import io
from utils import utils_image

class ObjectDetection:

    def __init__(self, model_name: str, temp_dir: str):
        (
            self.processor,
            self.model,
            self.device
        ) = self.load_model(model_name)
        self.set_image_temporary_directory(temp_dir)

    def load_model(self, model_name: str):
        processor = DetrImageProcessor.from_pretrained(model_name, revision="no_timm")
        model = DetrForObjectDetection.from_pretrained(model_name, revision="no_timm")

        # Set the device to GPU if available, otherwise use CPU
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)  # Move the model to the selected device

        return processor, model, device
    
    def set_image_temporary_directory(self, temp_dir):
        self.__temp_dir = temp_dir

    def detection(self, image_base64: str, category_to_detect: str):
        processor = self.processor
        model = self.model
        device = self.device

        return_images = []

        image_buffer = utils_image.convert_base64_to_bytesIO(image_base64)
        image = Image.open(image_buffer)

        if image.mode != "RGB":
            image = image.convert("RGB")

        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = model(**inputs)

        # convert outputs (bounding boxes and class logits) to COCO API
        # let's only keep detections with score > 0.9
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.9)[0]

        for label, box in zip(results["labels"], results["boxes"]):
            if model.config.id2label[label.item()] != category_to_detect:
                continue
            box = [round(i, 2) for i in box.tolist()]

            cropped_image = image.crop(box)
            return_images.append(utils_image.convert_pil_to_base64(cropped_image))

        response = {"images": return_images}
        return response