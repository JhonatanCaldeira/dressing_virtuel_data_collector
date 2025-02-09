import pytest
import numpy as np
import torch.nn.functional as F
import torch
from PIL import Image
from datasets import load_dataset
from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from sklearn.metrics import confusion_matrix

# Check for GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the processor and model
processor = SegformerImageProcessor.from_pretrained("sayeed99/segformer_b3_clothes")
model = AutoModelForSemanticSegmentation.from_pretrained("sayeed99/segformer_b3_clothes").to(device)
model.eval()

# Load the dataset
dataset = load_dataset("mattmdjaga/human_parsing_dataset", split="train")

def evaluate_segmentation(predictions, ground_truth, num_classes):
    confusion = confusion_matrix(ground_truth.flatten(), predictions.flatten(), labels=range(num_classes))
    pixel_accuracy = np.diag(confusion).sum() / confusion.sum()
    class_iou = np.diag(confusion) / (confusion.sum(axis=1) + confusion.sum(axis=0) - np.diag(confusion))
    mean_iou = np.nanmean(class_iou)
    return pixel_accuracy, mean_iou

@pytest.mark.parametrize("num_classes, expected_iou, expected_accuracy", [(17, 0.6, 0.9)])
def test_segmentation_model(num_classes, expected_iou, expected_accuracy):
    all_preds = []
    all_labels = []

    ds_train_test = dataset.train_test_split(test_size=0.02)
    ds_test = ds_train_test['test']

    for idx, sample in enumerate(ds_test):
        image = Image.fromarray(np.array(sample['image']))
        inputs = processor(images=image, return_tensors="pt").to(device)

        ground_truth = np.array(sample['mask'])

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            logits_resized = F.interpolate(
                logits,
                size=ground_truth.shape,
                mode="bilinear",
                align_corners=False
            )
            predictions = torch.argmax(logits_resized.squeeze(0), dim=0).cpu().numpy()

        all_preds.append(predictions)
        all_labels.append(ground_truth)

    all_preds = np.concatenate([p.flatten() for p in all_preds])
    all_labels = np.concatenate([l.flatten() for l in all_labels])

    pixel_accuracy, mean_iou = evaluate_segmentation(all_preds, all_labels, num_classes)

    assert mean_iou > expected_iou, f"Mean IoU is too low: {mean_iou}"
    assert pixel_accuracy > expected_accuracy, f"Pixel Accuracy is too low: {pixel_accuracy}"
