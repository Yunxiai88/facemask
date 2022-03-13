import json
import face_recognition

def get_embedding(file_stream):
    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(file_stream)

    filename = file_stream.filename

    # Find all the faces in the image
    face_locations = face_recognition.face_locations(image)
    print("I found {0} face(s) in photo {1}.".format(len(face_locations), filename))

    face_encoding = ""
    if len(face_locations) == 0:
        return {
            "code" : "1", 
            "message" : "No face found in this photo, Pls try another one."
        }
    elif len(face_locations) == 1:
        for face_location in face_locations:
            face_encoding = face_recognition.face_encodings(image, face_location)
            return {
                "code" : "0", 
                "message" : "face found.",
                "embedding" : face_encoding,
                "bbox" : face_location
            }
    else:
        return {
            "code: 2", 
            "message: There are more than one face in the photo, Pls try another one."
        }

    
