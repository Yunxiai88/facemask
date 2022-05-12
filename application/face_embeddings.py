import os
import json
from . import db
import numpy as np
from application import face_model, util
from .models import FaceEmbedding, IndividualPhoto, GroupPhoto

def get_faceEmbeddings(grp_photo_ids):
    face_embeddings = FaceEmbedding.query.filter(FaceEmbedding.grp_photo_id.in_(grp_photo_ids)).all()
    # print(face_embeddings[0])
    # for i in face_embeddings:
        # i.embedding = [float(j) for j in i.embedding[1:-1].split()]
        # i.face_bbox = [int(j) for j in i.face_bbox[1:-1].split(', ')]
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

def update_face_embedding(emb_ids, pred_indv_ids):
    try:
        pred_id_map = dict(zip(emb_ids, pred_indv_ids))
        print('updating face embedding: ', pred_id_map)

        face_emds = FaceEmbedding.query.filter(
            FaceEmbedding.id.in_([x for x in emb_ids]),
            FaceEmbedding.pred_indv_id == None
        )

        for face_emd in face_emds:
           FaceEmbedding.query.filter_by(id=face_emd.id).update({'pred_indv_id': pred_id_map.get(face_emd.id)})

        db.session.flush()
        return 0
    except Exception as e:
        print(e)
        return 1

def update_pred_indv_id(pred_indv_id, new_pred_indv_id):
    try:
        FaceEmbedding.query.filter_by(pred_indv_id = pred_indv_id).update({'pred_indv_id': new_pred_indv_id})
        db.session.flush()
        return 0
    except Exception as e:
        print(e)
        return 1

def update_faceembedding_with_matched_embedding(indvPhoto, embedding):
    try:
        group_faces = get_group_embeddings_by_indvId()
        if group_faces:
            known_face_encodings = [util.convert_embedding(f.embedding) for f in group_faces]
            face_encoding_to_check = util.convert_embedding(embedding)

            match_labels = face_model.is_face_matching(known_face_encodings, face_encoding_to_check)
            print("match labels: ", match_labels)

            face_mapping = [{
                'id':face.id, 
                'pred_indv_id': indvPhoto.id if match_labels[idx] == True else None} for idx, face in enumerate(group_faces)]
            print(json.dumps(face_mapping, indent=2))

            db.session.bulk_update_mappings(FaceEmbedding, face_mapping)

            db.session.flush()
        return 0
    except Exception as e:
        print(e)
        return 1
