import os
import json
import pathlib
from . import db
from sqlalchemy import null
from datetime import datetime

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
        face_list = [face.id for face in faces if face.deleted_at is None]
        print("All faces for current user: ", face_list)

    return render_template('profile.html', data=face_list, appends=2-len(face_list))

@profile.route('/upload')
@login_required
def profile_page():
    return render_template('face_image.html')

@profile.route('/update/<path:indvId>')
@login_required
def update_face(indvId):
    return render_template('face_image.html', indvId=indvId)

@profile.route('/query/<path:indvId>')
@login_required
def query_face(indvId):
    indvPhoto = IndividualPhoto.query.get(indvId)

    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER_INDV'], current_user.email)
    file_path = os.path.join(path.parent.parent, upload_path)

    # get file name
    file_name, _ = util.get_file_name_from_path(indvPhoto.file_path)

    return send_from_directory(file_path, file_name)

@profile.route('/delete/<path:indvId>')
@login_required
def delete_face(indvId):

    result_code = 1
    result_message = ""

    try:
        print('deleting individual id: ', indvId)
        #step1: delete from db
        indvPhoto = IndividualPhoto.query.get(indvId)
        if not indvPhoto:
            raise Exception("this person not exist. ")
        indvPhoto.deleted_at = datetime.now()

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
        result_code = util.delete_file(file_path, file_name)
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
            indvId = request.form['indvId']
            username = request.form['username']
            file = request.files['faceFile']

            #step1: get face embending
            data = face_model.get_embedding(file)
            if data["code"] != "0":
                raise Exception(data["message"])

            #check whehter same embedding with different id exist
            print('checking same person with id beginning...')
            individuals = photos.get_all_indv_photos()
            matched_ids = face_model.match_face_embedding (
                [util.convert_embedding(ind.embedding) for ind in individuals], 
                util.convert_embedding(data["embedding"]), 
                individuals
            )

            if matched_ids:
                filter_ids = [x for x in matched_ids if x != None]

                if filter_ids and current_user.id not in filter_ids:
                    raise Exception("same person used by different account, Please try another one.")
            print('checking same person with id end...\n')

            #step2: save file to disk
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER_INDV'], current_user.email)
            result = util.save_file(upload_path, file)
            if result == 1:
                raise Exception("file saved failed.")
            
            #step3: save to db
            indvPhoto = photos.save_IndividualPhoto(
                                    name      = username, 
                                    file_path = os.path.join(upload_path, file.filename),
                                    # file_name = file.filename,
                                    user_id   = current_user.id,
                                    embedding = data["embedding"],
                                    face_bbox = data["bbox"])
            if indvPhoto is None:
                raise Exception("save individual info to database failed.")
            
            #step4: match in group face embending
            res = face_embeddings.update_faceembedding_with_matched_embedding(indvPhoto, data["embedding"])
            if res == 1:
                raise Exception("match individual photo with group photos failed.")

            #step5: update individual table witn new id
            if indvId:
                res = photos.defunct_indv_photos(indvId)
                if res == 1:
                    raise Exception('update individual table failed.')

                # update face_embedding table witn new id
                res = face_embeddings.update_pred_indv_id(indvId, indvPhoto.id)
                if res == 1:
                    raise Exception('update face embedding table failed.')

            # save all transactions
            db.session.commit()

            print("file uploaded successful.")

            flash("file uploaded successful.")

            return redirect(url_for("profile.walk_face"))
        except Exception as e:
            print("System Error: ", e)

            # rollback -- delete saved individual file
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER_INDV'], current_user.email)
            result = util.delete_file(file_path, file.filename)
            if result == 1:
                print("delete file failed.")

            flash("System Error. Please contact administrator.")

            return redirect(url_for("profile.profile_page"))

