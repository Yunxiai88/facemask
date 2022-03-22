import json
from . import db
import os
from application import face_recognition
from .models import FaceEmbedding, IndividualPhoto, GroupPhoto

def get_faceEmbeddings(grp_photo_ids):
    face_embeddings = FaceEmbedding.query.filter(FaceEmbedding.grp_photo_id.in_(grp_photo_ids)).all()
    # print(face_embeddings[0])
    for i in face_embeddings:
        i.embedding = [float(j) for j in i.embedding[1:-1].split()]
        i.face_bbox = [int(j) for j in i.face_bbox[1:-1].split(', ')]
        # i.embedding = i.embedding[1:-1].map(lambda x : [float(x) for x in x.replace("[", "").replace ("]", "").split()], i.embedding)
        # i.face_bbox = i.face_bbox.map(lambda x : [float(x) for x in x.replace("(", "").replace (")", "").split()], i.embedding)
        # print(i.face_bbox)
        # print(type(i.embedding))
    return face_embeddings
    