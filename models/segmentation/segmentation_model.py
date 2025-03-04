from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
from utils import utils_image
import rembg
import torch.nn as nn
import torch
import numpy as np

class SegmentationModel():

    def __init__(self, 
                 model_name: str, 
                 temp_dir: str,
                 valid_labels: list[int] = [4, 5, 6, 7]):
        
        self.processor, self.model, self.device = self.load_model(model_name)
        self.set_valid_label(valid_labels)
        self.set_image_temporary_directory(temp_dir)

    def load_model(self, model_name: str):
        """
        Loads a pre-trained Segformer model and its corresponding image processor

        Args:
            model_name (str): The name of the pre-trained model to load

        Returns:
            tuple: A tuple containing the image processor, the pre-trained model,
                and the device (either GPU or CPU) to use for inference
        """
        processor = SegformerImageProcessor.from_pretrained(model_name)
        model = AutoModelForSemanticSegmentation.from_pretrained(model_name)

        # Set the device to GPU if available, otherwise use CPU
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)  # Move the model to the selected device

        return processor, model, device
    
    def set_valid_label(self, valid_labels: list[int]):
        self.__valid_labels = valid_labels
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

    def set_image_temporary_directory(self, temp_dir):
        self.__temp_dir = temp_dir

    def clothes_segmentation(self, image_path):
        """
        Segments clothing from a given image using a pre-trained semantic segmentation model.

        Args:
            image_path (str): The file path to the image that will be segmented.

        Returns:
            Tuple[torch.Tensor, AutoModelForSemanticSegmentation]: 
                - upsampled_logits (torch.Tensor): 
                The logits after upsampling to the original image size.
        """
        
        # Load the image processor and the pre-trained model for semantic segmentation
        processor = self.processor
        model = self.model
        device = self.device

        # Open and preprocess the image for the model
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

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

    def crop_clothes_from_fullbody(self, image_to_segment):
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
        device = self.device
        
        # Perform segmentation on the input image, returning logits 
        image_to_segment = utils_image.convert_base64_to_bytesIO(image_to_segment)
        upsampled_logits = self.clothes_segmentation(image_to_segment)
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
        image = self.remove_background(Image.open(image_to_segment))    

        for label in unique_labels:
            # Skip labels that are not in the valid_labels list
            if label not in self.__valid_labels:
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

            return_images.append(utils_image.convert_pil_to_base64(cropped_image))

        response = {"images": return_images}
        return response 

    def remove_background(self, image: Image):
        """
        Removes the background from the given image using the rembg library.

        Args:
            image (Image): The input image from which the background will be removed.

        Returns:
            Image: The image with the background removed.
        """
        input_array = np.array(image)
        output_array = rembg.remove(input_array, bgcolor=(255, 255, 255, 255))
        return Image.fromarray(output_array)

    def crop_clothes(self, image_to_segment: str):
        """
        Segments clothing from a single clothe image and crops out the 
        detected clothing.

        Args:
            image_to_segment (str): The file path to the full-body 
            image that will be segmented.

        Returns:
            List[str]: Return a list of paths to the temporary images.
        """

        image_to_segment = utils_image.convert_base64_to_bytesIO(image_to_segment)
        upsampled_logits = self.clothes_segmentation(image_to_segment)

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

        return_images = []

        image = Image.open(image_to_segment)
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

        return_images.append(utils_image.convert_pil_to_base64(cropped_image))

        response = {"images": return_images}
        return response 