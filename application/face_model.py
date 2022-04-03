import cv2
import json
import numpy as np
import face_recognition

from flask import session
from datetime import datetime
from sklearn.cluster import DBSCAN
from flask_login import current_user

from application import util, photos, clustering

def get_embedding(file_stream):
    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(file_stream)

    filename = file_stream.filename
    print("Processing photo: {0}\n".format(filename))

    # Find all the faces in the image
    print("Detecting faces start at {0}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))

    # Find all the faces in the image using the default HOG-based model.
    # This method is fairly accurate, but not as accurate as the CNN model and not GPU accelerated.
    face_locations = face_recognition.face_locations(image, model="hog")

    print("I found {0} face(s) at {1}\n".format(len(face_locations), datetime.now().strftime("%m/%d/%Y %H:%M:%S")))

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
            "code": "2", 
            "message": "There are more than one face in the photo, Pls try another one."
        }

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

###########################################################################
# Start Clustering of Faces in Group Photos
#
###########################################################################
def clustering_group_photos(admin_id):
    # get all photos uploaded by the admin
    all_grp_photos = photos.get_all_grp_photos(admin_id)
    # get all face_embedding data of the queried photos
    [all_embeddings, emb_ids, grp_ids, img_pths, bboxes] = map(list,zip(*[([float(j) for j in embed.embedding[1:-1].split()], embed.id, i.id, i.file_path, [int(k) for k in embed.face_bbox[1:-1].split(', ')]) for i in all_grp_photos for embed in i.face_embeddings]))
    # print(all_embeddings, emb_ids, grp_ids, img_pths, bboxes)
    print("type of all_embeddings: {0}, len is {1}".format(type(all_embeddings), len(all_embeddings)))
    
    try:
        # cluster embeddings
        clt = DBSCAN(metric="euclidean")
        clt.fit(all_embeddings)

        # determine the total number of unique faces found in the dataset
        all_labels = clt.labels_
        # clusterIDs = np.unique(all_labels)
        # print('all labels: ', all_labels)
        # print('unique ids: ', clusterIDs)

        no_face_index = []
        # check if unknown label has a face
        unknown_faces = np.where(all_labels == -1)[0]
        for f in unknown_faces:
            grp_image_path = img_pths[f]
            print(grp_image_path)
            
            grp_image = cv2.imread(grp_image_path)
            [top, right, bottom, left] = bboxes[f]
            roi = grp_image[top:bottom, left:right]
            rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            face = face_recognition.face_locations(rgb)
            # if not a face, delete it
            if not face:
                no_face_index.append(f)
                # all_labels = np.delete(all_labels, f)
                # del all_embeddings[f]
                # del emb_ids[f]
                # del grp_ids[f]
        print("no face index: ", no_face_index)

        all_labels = util.delete_list_by_index(all_labels, no_face_index)
        emb_ids = util.delete_list_by_index(emb_ids, no_face_index)
        grp_ids = util.delete_list_by_index(grp_ids, no_face_index)
        # print('unique ids: ', np.unique(all_labels))
        print("grp_ids --- ", grp_ids)
        # Add clustering results in DB
        res = clustering.add_clustering_results(emb_ids, grp_ids, all_labels)

        if res == 1:
            print("Saving clustering results to DB failed.")

            return 1

        return 0

    except Exception as e:
        print(e)

        return 1

###########################################################################
# method to check face encoding against a list of know face encodings
#
###########################################################################
def is_face_matching(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    print("matching individual face with group photo")
    match_label = face_recognition.compare_faces(known_face_encodings, face_encoding_to_check, tolerance)
    return match_label

###########################################################################
# mark all faces except selected in a photo
#
###########################################################################
def mark_face(indv_ids):
    photo_ids = []
    need_process_ids = []

    # get all photos should be returned
    group_photos = photos.get_grp_photo_by_indvId(indv_ids)
    photo_ids = [util.get_file_name_from_path(photo.file_path)[0] for photo in group_photos]

    # check whether id has been processed before
    processed_ids = session.get("processed_ids")
    if processed_ids:
        print("photos of persons:{0} have been processed: ".format(processed_ids))

        need_process_ids = [ind for ind in indv_ids if ind not in processed_ids]
        if not need_process_ids:
            return photo_ids
        else:
            indv_ids = need_process_ids
            print("will process photos for persons:{0}".format(need_process_ids))
    else:
        session["processed_ids"] = indv_ids
    
    # process filter photos
    if group_photos:
        for photo in group_photos:
            # file_name = util.get_unique_name()
            file_name = util.get_file_name_from_path(photo.file_path)[0]

            grp_image = cv2.imread(photo.file_path)
            print("marking photo: ", photo.file_path)

            embeddings = photo.face_embeddings
            for face in embeddings:
                if str(face.pred_indv_id) not in indv_ids:
                    [top, right, bottom, left] = util.convert_bbox(face.face_bbox)
                    grp_image[top:bottom, left:right] = cv2.blur(grp_image[top:bottom, left:right], (40, 40))
            # write photo with mask
            cv2.imwrite('processed/{0}/{1}'.format(current_user.email, file_name), grp_image)
    else:
        print("no group photo for selected person.")

    return photo_ids