import os
import json
from . import db
import numpy as np
from datetime import datetime
from itertools import groupby

from application import face_model, util, photos
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

def get_all_face_embeddings():
    face_embeddings = FaceEmbedding.query.all()
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
        print("Matching faces start at {0}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
        # get all face_embeddings of available group photos
        group_faces = get_all_face_embeddings()
        indv_faces = photos.get_all_indv_photos(indvPhoto.user_id)

        # get average face embedding
        known_face_encodings = []
        individual_list = [individual for individual in indv_faces if individual.deleted_at is None]
        sorted_individuals = sorted(individual_list, key=lambda indiv: indiv.name)

        for k, v in groupby(sorted_individuals, key=lambda indiv: indiv.name):
            known_face_encodings.append(np.mean([util.convert_embedding(f.embedding) for f in list(v)], axis=0))
        print(known_face_encodings)
        #known_face_encodings = [util.convert_embedding(f.embedding) for f in indv_faces]

        if group_faces:
            matched_data = {}
            
            group_faces_encodings = [util.convert_embedding(f.embedding) for f in group_faces]
            for i, k_em in enumerate(known_face_encodings):
                match_labels = face_model.is_face_matching(group_faces_encodings, k_em)
            
                if True in match_labels:
                    # print(matches)
                    match_idx = [j for j, x in enumerate(match_labels) if x]
                    matched_data[i] = match_idx

            print('matched_data - ', matched_data)

            # check if any embeddings is matched to multiple faces
            conflicting_embeddings = util.has_duplicates(matched_data)
            print('conflicting_embeddings - ',conflicting_embeddings)

            # if yes, then again match that embedding against the matched face and select shortest distance
            if conflicting_embeddings:
                for emb_idx, kn_face_idxs in conflicting_embeddings.items():
                    kn_embs = [known_face_encodings[i] for i in kn_face_idxs]
                    distances = face_model.face_distance(kn_embs,np.array(group_faces_encodings[emb_idx]))
                    best_match = kn_face_idxs[np.argmin(distances)]
                    # remove the idx from other matches, except for best_match
                    for i in kn_face_idxs:
                        if i != best_match:
                            matched_data[i].remove(emb_idx)
            print('matched_data2 - ', matched_data)
            # Save the matched face id (indv_photo_id) to cluster table and face_embeddings table
            face_mapping = []
            for kn_emb_idx, grp_emb_idxs in matched_data.items():
                for emb_idx in grp_emb_idxs:
                    face_embed_data = {'id': group_faces[emb_idx].id, 'pred_indv_id': indv_faces[kn_emb_idx].id}
                    face_mapping.append(face_embed_data)
            
            print('face_mapping: ',face_mapping)

            db.session.bulk_update_mappings(FaceEmbedding, face_mapping)

            db.session.flush()
        print("Matching faces end at {0}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
        return 0
    except Exception as e:
        print(e)
        return 1
