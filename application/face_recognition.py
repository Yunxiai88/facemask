import face_recognition
import numpy as np
import pickle
import cv2
import os
from sklearn.cluster import DBSCAN
import face_recognition


###########################################################################
# Get all faces in a photo saved in disk
#
###########################################################################
def get_all_faces(filepath):

  image = cv2.imread(filepath)
  rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

  # detect the (x, y)-coordinates of the bounding boxes corresponding to each face in the input image
  boxes = face_recognition.face_locations(rgb)

  # compute the facial embedding for the face
  encodings = face_recognition.face_encodings(rgb, boxes)

  return boxes, encodings

###############
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

