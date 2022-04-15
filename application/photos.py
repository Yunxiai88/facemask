import os
import json

from . import db
from sqlalchemy import delete
from application import face_model, face_embeddings
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

        db.session.flush()
        return individualPhoto
    except Exception as e:
        print(e)
        return None

def get_all_indv_photos(user_id=None):
    try:
        query = IndividualPhoto.query.filter(IndividualPhoto.deleted_at == None)
        if user_id:
            query = query.filter(IndividualPhoto.user_id == user_id)
        return query.all()
    except Exception as e:
        print(e)
        return 1

def delete_indv_photos(indv_id):
    try:
        IndividualPhoto.query.filter_by(id == indv_id).delete()
        db.session.flush()
        return 0
    except Exception as e:
        print(e)
        return 1

def save_GroupPhotos(file_paths, admin_id):
    try:
        face_data = []
        for file_path in file_paths:
            print("save group photo for {0}".format(file_path))
            groupPhoto = GroupPhoto(file_path, admin_id, None)
            db.session.add(groupPhoto)
            db.session.flush()

            print("get all faces for {0}".format(file_path))
            boxes, embeddings = face_model.get_all_faces(file_path)
            d = [{'grp_photo_id':groupPhoto.id, 'face_bbox':str(box), 'embedding':str(emb), 'pred_indv_id': None} for (box, emb) in zip(boxes, embeddings)]
            face_data.extend(d)
            groupPhoto.no_of_faces = len(d)
        db.session.bulk_insert_mappings(FaceEmbedding, face_data)
        # db.session.commit()
        return face_data
    except Exception as e:
        print(e)
        return 1

def get_grp_photo(grp_photo_id):
    try:
        grp_photo = GroupPhoto.query.filter_by(id=grp_photo_id).first()
        print("group photo - ", grp_photo.id)
        return grp_photo
    except Exception as e:
        print(e)
        return 1

def get_all_grp_photos(admin_id):
    try:
        grp_photo = GroupPhoto.query.filter_by(admin_id=admin_id).all()
        print("there are {0} photos".format(len(grp_photo)))
        return grp_photo
    except Exception as e:
        print(e)
        return 1

def delete_grp_photo(grp_photo_ids):
    try:
        embeddings = face_embeddings.get_faceEmbeddings(grp_photo_ids)
        for fe in embeddings:
            FaceEmbedding.query.filter_by(id=fe.id).delete()

        GroupPhoto.query.filter(GroupPhoto.id.in_(grp_photo_ids)).delete()
        db.session.flush()
        return 0
    except Exception as e:
        print(e)
        return 1

###########################################################################
# Get all group photos base on selected person
#
###########################################################################
def get_grp_photo_by_indvId(indv_id_list):
    try:
        grp_photo = GroupPhoto.query.filter(GroupPhoto.face_embeddings.any(FaceEmbedding.pred_indv_id.in_(indv_id_list))).all()
        print("there are {0} photos".format(len(grp_photo)))
        return grp_photo
    except Exception as e:
        print(e)
        return None