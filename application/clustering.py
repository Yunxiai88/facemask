import json
from . import db
import numpy as np
from .models import ClusteringLog, Cluster
from flask_login import current_user
from sqlalchemy.orm import joinedload

def add_clustering_results(emb_ids, grp_photo_ids, clt_labels):
  print("grp_photo_ids ----- ", grp_photo_ids)
  try:
    cluster_ids = np.unique(clt_labels)
    g = str(grp_photo_ids)
    x = str(cluster_ids)
    print("cluster_ids: ", cluster_ids)
    print("user_id: ", current_user.id)

    # insert record in clustering_log table
    clustering_log = ClusteringLog(g, len(cluster_ids), x, current_user.id)
    db.session.add(clustering_log)
    db.session.flush()

    print(clustering_log.id)

    # insert records in cluster table
    face_data = []
    for cluster_id in cluster_ids:
      idxs = np.where(clt_labels == cluster_id)[0]
      print(cluster_id)
      for i in idxs:
        each_face_data = {
          'cluster_no': cluster_id,
          'clustering_log_id': clustering_log.id,
          'face_embedding_id': emb_ids[i],
          'pred_indv_id': None
        }
        face_data.append(each_face_data)
    db.session.bulk_insert_mappings(Cluster, face_data)
    db.session.commit()
    return 0
  
  except Exception as e:
    print(e)
    return 1


