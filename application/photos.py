import json
from . import db
import face_recognition

from .models import FaceEmbedding, IndvPhoto

def get_embedding(file_stream):
    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(file_stream)

    filename = file_stream.filename

    # Find all the faces in the image
    face_locations = face_recognition.face_locations(image, model="hog")
    print("I found {0} face(s) in photo {1}.".format(len(face_locations), filename))

    face_encoding = ""
    if len(face_locations) == 0:
        return {
            "code" : "1", 
            "message" : "No face found in this photo, Pls try another one."
        }
    elif len(face_locations) == 1:
        face_encodings = face_recognition.face_encodings(image, face_locations)

        print("face location = ", face_locations[0])
        print("face encoding = ", face_encodings[0])

        return {
            "code" : "0", 
            "message" : "face found.",
            "embedding" : str(face_encodings[0]),
            "bbox" : str(face_locations[0])
        }
    else:
        return {
            "code: 2", 
            "message: There are more than one face in the photo, Pls try another one."
        }

def save_faceEmbedding(embedding, bbox, group_photo_id=None, indv_photo_id=None):
    faceEmbedding = FaceEmbedding(embedding, bbox, group_photo_id, indv_photo_id)
    db.session.add(faceEmbedding)
    db.session.commit()

def save_IndividualPhoto(name, file_path, file_name, uploaded_by, embedding, bbox, group_photo_id=None):
    try:
        individualPhoto = IndvPhoto(name, file_path, file_name, uploaded_by)
        db.session.add(individualPhoto)
        db.session.flush()

        print("Temp Individual ID = ", individualPhoto.id)

        faceEmbedding = FaceEmbedding(embedding, bbox, group_photo_id, individualPhoto.id)
        db.session.add(faceEmbedding)
        db.session.flush()

        db.session.commit()
        return 0
    except Exception as e:
        print(e)
        return 1
