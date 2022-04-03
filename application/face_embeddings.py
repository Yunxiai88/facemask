import os
import json
from . import db
import numpy as np
from application import face_model
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

###########################################################################
# Get group face embeddings by selected person
#
###########################################################################
def get_group_embeddings_by_indvId(pred_indv_id = None):
    face_embeddings = FaceEmbedding.query.filter(FaceEmbedding.pred_indv_id == pred_indv_id).all()
    return face_embeddings
