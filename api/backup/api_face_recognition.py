from fastapi import Depends, FastAPI, HTTPException, Security, File, UploadFile, Response
from fastapi.security.api_key import APIKey, APIKeyHeader
from fastapi.responses import FileResponse
from pathlib import Path
from PIL import Image
import face_recognition
import shutil
import tempfile
import io
import zipfile
import os

PREFIX = os.getenv("FACE_RECOGNITION_API_ENDPOINT")
API_KEY = os.getenv("FACE_RECOGNITION_API_KEY")
TMP_DIR = os.getenv("IMAGE_TMP_DIR")

app = FastAPI()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, 
            detail="Could not validate API KEY"
        )

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}


@app.post(f"/{PREFIX}/face_detection")
def crop_object_image(image: UploadFile = File(...),
                      images_to_search: UploadFile = File(...),
                      api_key: APIKey = Depends(get_api_key)):

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        temp_image_path = temp_dir_path / image.filename
        temp_zip_path = temp_dir_path / images_to_search.filename

        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(images_to_search.file, buffer)

        with open(temp_zip_path, "rb") as zip_file:
            zip_file_bytes = io.BytesIO(zip_file.read())

        with zipfile.ZipFile(zip_file_bytes) as zf:
            for info in zf.infolist():
                if (not info.filename.endswith(".jpg") and 
                    not info.filename.endswith(".png")):
                    continue

                with zf.open(info) as zimage:
                    picture_of_me = face_recognition.load_image_file(temp_image_path)
                    my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]

                    # my_face_encoding now contains a universal 'encoding' of my facial features
                    # that can be compared to any other picture of a face!

                    try:
                        zimage_data = zimage.read()
                        unknown_picture = face_recognition.load_image_file(io.BytesIO(zimage_data))
                        unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]

                        # Now we can see the two face encodings are of the same person with `compare_faces`!
                        results = face_recognition.compare_faces(
                            unknown_face_encoding, [my_face_encoding])
                        if results[0] == True:
                            b = io.BytesIO(zimage_data)
                            pil_image = Image.open(b)
                            pil_image.save(TMP_DIR +'/'+ info.filename)
                            return FileResponse(TMP_DIR +'/'+ info.filename)
                    except IndexError:
                        print("I wasn't able to locate any faces in at least one of the images.")
                        continue

    return {'image': ''}
