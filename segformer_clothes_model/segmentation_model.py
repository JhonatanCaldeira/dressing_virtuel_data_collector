from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
import matplotlib.pyplot as plt
import torch.nn as nn
import torch
import numpy as np
import base64


def clothes_segmentation(image_to_segment):
    print("Loading Model")

    processor = SegformerImageProcessor.from_pretrained("sayeed99/segformer_b3_clothes")
    model = AutoModelForSemanticSegmentation.from_pretrained("sayeed99/segformer_b3_clothes")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device) # Move the model to the selected device

    # Open and preprocess the image
    image = Image.open(image_to_segment)
    inputs = processor(images=image, return_tensors="pt")

    # Move inputs to the same device as the model
    inputs = {k: v.to(device) for k, v in inputs.items()}

    outputs = model(**inputs)
    logits = outputs.logits

    upsampled_logits = nn.functional.interpolate(
        logits,
        size=image.size[::-1],
        mode="bilinear",
        align_corners=False,
    )

    image.close()

    return upsampled_logits, model

def crop_clothes(image_to_segment):
    upsampled_logits, model = clothes_segmentation(image_to_segment)

    # Get the segmentation map
    pred_seg = upsampled_logits.argmax(dim=1)[0].cpu().numpy()

    # Get unique class labels present in the predicted segmentation map
    unique_labels, counts = np.unique(pred_seg, return_counts=True)

    # Create a dictionary to store label counts excluding label 0 (Background)
    label_counts = {label: count for label, count in 
                    zip(unique_labels, counts) if label != 0}

    # Get the label with the most values
    max_label = max(label_counts, key=label_counts.get)

    # Print the results
    # print(f"Label counts: {label_counts}")
    # print(f"Label with the most values: {max_label}, Count: {label_counts[max_label]}")

    image = Image.open(image_to_segment)

    # Convert the segmentation map to a binary mask 
    target_class = max_label
    binary_mask = (pred_seg == target_class).astype(np.uint8)

    # Create a blank (transparent) image with the same size as the original image
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

    # Show the cropped image
    # plt.imshow(cropped_image)
    # plt.axis('off')
    # plt.show()

    image.close()


if __name__ == "__main__":
    clothes_segmentation('segformer_clothes_model/images/100_0519.JPG')