from schemas import schema
from database.connection import SessionLocal, engine
from database.crud import insert_metrics
from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from datasets import load_dataset
from sklearn.metrics import confusion_matrix
from PIL import Image
import torch.nn.functional as F
import torch
import numpy as np

# Check for GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load the processor and model
processor = SegformerImageProcessor.from_pretrained("sayeed99/segformer_b3_clothes")
model = AutoModelForSemanticSegmentation.from_pretrained("sayeed99/segformer_b3_clothes").to(device)
model.eval()

# Load the dataset (replace 'test' with your desired split)
dataset = load_dataset("mattmdjaga/human_parsing_dataset", split="train")

# Function to calculate metrics
def evaluate_segmentation(predictions, ground_truth, num_classes):
    confusion = confusion_matrix(ground_truth.flatten(), predictions.flatten(), labels=range(num_classes))
    pixel_accuracy = np.diag(confusion).sum() / confusion.sum()
    class_iou = np.diag(confusion) / (confusion.sum(axis=1) + confusion.sum(axis=0) - np.diag(confusion))
    mean_iou = np.nanmean(class_iou)
    return pixel_accuracy, mean_iou, class_iou

def evaluate_model():
    num_classes = 17
    all_preds = []
    all_labels = []

    ds_train_test = dataset.train_test_split(test_size=0.02)
    ds_test = ds_train_test['test']

    for idx, sample in enumerate(ds_test):
        # Preprocess the image
        image = Image.fromarray(np.array(sample['image']))
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        # Get ground truth mask
        ground_truth = np.array(sample['mask'])
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits 
            # Resize logits to match mask size
            logits_resized = F.interpolate(
                logits, 
                size=ground_truth.shape,
                mode="bilinear",
                align_corners=False
            )
            predictions = torch.argmax(logits_resized.squeeze(0), dim=0).cpu().numpy() 
        
        # Store predictions and labels
        all_preds.append(predictions)
        all_labels.append(ground_truth)

    all_preds = np.concatenate([p.flatten() for p in all_preds])
    all_labels = np.concatenate([l.flatten() for l in all_labels])

    # Evaluate
    pixel_accuracy, mean_iou, class_iou = evaluate_segmentation(all_preds, all_labels, num_classes)

    print(f"Pixel Accuracy: {pixel_accuracy:.4f}")
    print(f"Mean IoU: {mean_iou:.4f}")
    print(f"Per-Class IoU: {class_iou}")

    return {
        "mean_iou": mean_iou,
        "pixel_accuracy": pixel_accuracy,
    }

if __name__ == "__main__":
    # Perform model evaluation
    metrics = evaluate_model()

    # Update Prometheus metrics
    for metric_name, value in metrics.items():
        schema_metrics = schema.Metrics(
            name=metric_name,
            value=str(value)
        )

        db_return = insert_metrics(db=SessionLocal(), metrics=schema_metrics)