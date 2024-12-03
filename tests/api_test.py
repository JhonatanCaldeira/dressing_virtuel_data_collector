from PIL import Image
import pytest
from fastapi.testclient import TestClient
from api import api_models
from unittest.mock import patch
from utils import utils_image
import os

MODELS_API_ENDPOINT = os.getenv("MODELS_API_ENDPOINT")
MODELS_API_KEY = os.getenv("MODELS_API_KEY")

client = TestClient(api_models.app)

@pytest.fixture
def mock_image_file():
    """Fixture to create a mock image file."""
    from io import BytesIO
    return BytesIO(b"fake image content")

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_crop_object_image_success():
    """Test a successful object detection API call."""
    # Mocking the base64 conversion and detection result

    image = "tests/images/object_detection.jpg"

    with open(image, "rb") as image_file:
        response = client.post(
            f"/{MODELS_API_ENDPOINT}/object_detection", 
            files={"image": (image, image_file, utils_image.get_mime_type(image))},
            data={"category_to_detect": "person"},
            headers={"access_token": MODELS_API_KEY}
        )

    assert response.status_code == 200

def test_crop_object_image_no_images():
    """Test when no images are detected in the response."""
    image = "tests/images/object_detection.jpg"

    with open(image, "rb") as image_file:
        response = client.post(
            f"/{MODELS_API_ENDPOINT}/object_detection", 
            files={"image": (image, image_file, utils_image.get_mime_type(image))},
            data={"category_to_detect": "cat"},
            headers={"access_token": MODELS_API_KEY}
        )
    assert response.status_code == 204

def test_face_detection_success():
    image_face_id = Image.open("tests/images/faceid.jpg")
    images_to_search = Image.open("tests/images/unknown_face_1.jpg")

    image_b64 = utils_image.convert_pil_to_base64(image_face_id)
    images_to_search_b64 = utils_image.convert_pil_to_base64(images_to_search)

    image = utils_image.convert_base64_to_bytesIO(image_b64)
    images_to_search = utils_image.convert_base64_to_bytesIO(images_to_search_b64)

    files = {"image": ('faceid.jpeg', 
                       image,
                       utils_image.get_mime_type('faceid.jpg')),
            "images_to_search" : ('unknown_face_1.jpeg',
                                  images_to_search,
                                  utils_image.get_mime_type(
                                      'unknown_face_1.jpg'))}
    response = client.post(
        f"/{MODELS_API_ENDPOINT}/face_detection", 
        files=files,
        headers={"access_token": MODELS_API_KEY}
    )

    assert response.status_code == 200

def test_segmentation_success():
    image = Image.open("tests/images/segmentation.jpg")

    image_b64 = utils_image.convert_pil_to_base64(image)

    image = utils_image.convert_base64_to_bytesIO(image_b64)

    files = {"image": ('segmentation.jpg', 
                       image, 
                       utils_image.get_mime_type('segmentation.jpg'))}
    response = client.post(
        f"/{MODELS_API_ENDPOINT}/clothes_segmentation", 
        files=files,
        headers={"access_token": MODELS_API_KEY}
    )

    assert response.status_code == 200