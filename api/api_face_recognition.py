from fastapi import Depends, FastAPI, HTTPException, Security, File, UploadFile, Response, Form
from fastapi.security.api_key import APIKey, APIKeyHeader
from fastapi.responses import FileResponse
from starlette.status import HTTP_403_FORBIDDEN
from pathlib import Path
from PIL import Image
import face_recognition
import yaml
import shutil
import tempfile
import io
import zipfile
import os

def load_config(filepath='config/config.yaml'):
    """
    Loads the webservice configuration from a YAML file.

    Args:
        filepath (str): Path to the YAML configuration file.

    Returns:
        dict: A dictionary containing the database configuration.
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config['webservice_face_recognition']

# Load database configuration from the YAML file
ws_config = load_config()

PREFIX = ws_config['prefix']
API_KEY = ws_config['API_KEY'] #REVOIR APRES

app = FastAPI()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header   
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
    
def zipfiles(filenames):
    zip_filename = "archive.zip"

    s = io.BytesIO()
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)

        # Add file, at correct path
        zf.write(fpath, fname)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = Response(s.getvalue(), 
                    media_type="application/x-zip-compressed", 
                    headers={'Content-Disposition': f'attachment;filename={zip_filename}'
        })

    return resp

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
                if (info.filename.endswith(".jpg") or 
                    info.filename.endswith(".png")):
                        
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
                                results = face_recognition.compare_faces(unknown_face_encoding,[my_face_encoding])
                                if results[0] == True:
                                    b = io.BytesIO(zimage_data)
                                    pil_image = Image.open(b)
                                    pil_image.save('/home/jcaldeira/dressing_virtuel_data_collector/media/tmp/detection/' + info.filename)
                                    print("It's a picture of me!")
                                    return FileResponse('/home/jcaldeira/dressing_virtuel_data_collector/media/tmp/detection/' + info.filename)
                                else:
                                    print("It's not a picture of me!")
                            except IndexError:
                                print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
                                continue
        
    return {'image': ''}