import json
from . import db
import os
from application import face_recognition
from .models import FaceEmbedding, IndividualPhoto, GroupPhoto

# def save_faceEmbedding(embedding, bbox, group_photo_id=None, indv_photo_id=None):
#     faceEmbedding = FaceEmbedding(embedding, bbox, group_photo_id, indv_photo_id)
#     db.session.add(faceEmbedding)
#     db.session.commit()

def save_IndividualPhoto(name, file_path, user_id, embedding, face_bbox):
    try:
        individualPhoto = IndividualPhoto(name, file_path, user_id, embedding, face_bbox)
        db.session.add(individualPhoto)
        db.session.flush()

        print("Temp Individual ID = ", individualPhoto.id)

        db.session.commit()
        return 0
    except Exception as e:
        print(e)
        return 1

def save_GroupPhotos(file_paths, admin_id):
    try:
        face_data = []
        for file_path in file_paths:
            groupPhoto = GroupPhoto(file_path, admin_id, None)
            db.session.add(groupPhoto)
            db.session.flush()
            boxes, embeddings = face_recognition.get_all_faces(file_path)
            d = [{'grp_photo_id':groupPhoto.id, 'face_bbox':str(box), 'embedding':str(emb), 'indv_id': None} for (box, emb) in zip(boxes, embeddings)]
            face_data.extend(d)
            groupPhoto.no_of_faces = len(d)
        db.session.bulk_insert_mappings(FaceEmbedding, face_data)
        db.session.commit()
        return 0
    except Exception as e:
        print(e)
        return 1