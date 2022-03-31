import os
import json
import pathlib
from . import db
from sqlalchemy import null

from .models import IndividualPhoto, FaceEmbedding
from application import util, users, photos, face_model, face_embeddings

from flask_login import current_user, login_required
from flask import Blueprint, flash, jsonify, current_app, session
from flask import render_template, request, redirect, url_for, send_from_directory

profile = Blueprint('profile', __name__, url_prefix='/profile')

path = pathlib.Path(__file__)

@profile.route('/')
@login_required
def walk_face():
    faces = current_user.uploaded_indv_photos

    face_list = []

    if faces:
        face_list = [face.id for face in faces]
        print("All faces for current user: ", face_list)

    return render_template('profile.html', data=face_list, appends=2-len(face_list))

@profile.route('/upload')
@login_required
def profile_page():
    return render_template('face_image.html')

@profile.route('/query/<path:indvId>')
@login_required
def query_face(indvId):
    indvPhoto = IndividualPhoto.query.get(indvId)

    file_name, file_path = util.get_file_name_from_path(indvPhoto.file_path)
    file_path = os.path.join(path.parent.parent, file_path)

    return send_from_directory(file_path, file_name)

@profile.route('/delete/<path:indvId>')
@login_required
def delete_face(indvId):

    result_code = 1
    result_message = ""

    try:
        #step1: delete from db
        indvPhoto = IndividualPhoto.query.get(indvId)
        db.session.delete(indvPhoto)
        db.session.flush()
        print("1 --> delete individual photo [{}] from db.".format(indvId))

        #step2: delete individual face embedding
        for aa in db.session.query(FaceEmbedding).\
                            filter(FaceEmbedding.pred_indv_id == indvId).\
                            filter(FaceEmbedding.grp_photo_id == None):
            print("-------", str(aa.embedding))

            db.session.delete(aa)
            db.session.flush()
        print("2 --> delete individual face embedding from db.")

        #step3: update individual id for group photos
        embeddings = FaceEmbedding.query.filter(
                    FaceEmbedding.grp_photo_id != None
                ).filter(
                    FaceEmbedding.pred_indv_id == indvId
                ).all()

        if embeddings:
            print("Having group embeddings to update.")
            for bb in embeddings:
                bb.pred_indv_id = None
            db.session.flush()
            print("3 --> update individual related group embedding in db.")

        #step4: remove file from disk
        file_name, file_path = util.get_file_name_from_path(indvPhoto.file_path)
        result_code = util.delete_processed_file(file_name)
        if result_code == 1:
            print("delete file failed.")
        else:
            print("4 --> remove individual photo from disk.")

            #step5: final delete record from db
            db.session.commit()
            print("5 --> final delete individual info.")

            result_message = "Delete individual photo successful."
    except Exception as e:
        print("System Error: [{}] -- {}".format(delete_face, e))
        result_message = "delete individual photo failed."

    flash(result_message)

    return redirect(url_for("profile.walk_face"))

@profile.route('/upload', methods = ['POST'])
@login_required
def upload_face():
    if request.method == "POST":
        try:
            username = request.form['username']
            file = request.files['faceFile']

            #step1: get face embending
            data = face_model.get_embedding(file)
            # print("embedding info: " + str(data))

            #data = json.loads(data_str)

            if data["code"] != "0":
                return jsonify({"error": data["message"]})

            #step2: save file to disk
            result = util.save_processed_file(file)
            if result == 1:
                print("file saved failed.")
                return jsonify({"error": "file uploaded failed."})
            
            #step3: save to db
            indvPhoto = photos.save_IndividualPhoto(
                                    name      = username, 
                                    file_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email, file.filename),
                                    # file_name = file.filename,
                                    user_id   = current_user.id,
                                    embedding = data["embedding"],
                                    face_bbox = data["bbox"])
            if indvPhoto is None:
                print("save info to database failed.")

                # delete uploaded file
                result = util.delete_processed_file(file.filename)
                if result == 1:
                    print("delete file failed.")

                # return error message
                return jsonify({"error": "file uploaded failed."})
            
            #step4: match in group face embending
            group_faces = face_embeddings.get_group_faceEmbeddings_by_indvId()
            if group_faces:
                known_face_encodings = [face_embeddings.convert_embedding(f.embedding) for f in group_faces]
                face_encoding_to_check = face_embeddings.convert_embedding(data["embedding"])

                match_labels = face_model.is_face_matching(known_face_encodings, face_encoding_to_check)
                print("match labels: ", match_labels)

                face_mapping = [{
                    'id':face.id, 
                    'pred_indv_id': indvPhoto.id if match_labels[idx] == True else None} for idx, face in enumerate(group_faces)]
                print(face_mapping)

                db.session.bulk_update_mappings(FaceEmbedding, face_mapping)
                db.session.commit()

            print('file uploaded successful.')
            return jsonify({'message': "successful"})
        except Exception as e:
            print("System Error: ", e)
            return jsonify({"error": "System Error. Please contact administrator."})

