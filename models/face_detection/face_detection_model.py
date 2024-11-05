from PIL import Image
from utils import utils_image
import face_recognition

class FaceDetectionModel():

    def __init__(self, 
                 temp_dir: str):
        
        self.set_image_temporary_directory(temp_dir)
    
    def set_image_temporary_directory(self, temp_dir):
        self.__temp_dir = temp_dir

    def face_recognition(self, face_id_base64, image_base64):
        face_id = utils_image.convert_base64_to_bytesIO(face_id_base64)
        unknown = utils_image.convert_base64_to_bytesIO(image_base64)

        picture_of_me = face_recognition.load_image_file(face_id)
        my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
        response = {"images":''}
        try:
            unknown_picture = face_recognition.load_image_file(unknown)
            unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]

            # Now we can see the two face encodings are of the same person with `compare_faces`!
            results = face_recognition.compare_faces(
                unknown_face_encoding, [my_face_encoding])
            if results[0] == True:
                response = {"images": utils_image.convert_pil_to_base64(Image.open(unknown))}
        except IndexError:
            print("I wasn't able to locate any faces in at least one of the images.")
            
        return response