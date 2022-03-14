import os
import pathlib
from . import db
from sqlalchemy import null

from .models import IndvPhoto, FaceEmbedding
from application import util, users, photos

from flask_login import current_user
from flask import Blueprint, flash, jsonify, current_app, session
from flask import render_template, request, redirect, url_for, send_from_directory

profile = Blueprint('profile', __name__, url_prefix='/profile')

path = pathlib.Path(__file__)

@profile.route('/')
def walk_face():
    faces = current_user.indvPhotos

    face_list = []

    if faces:
        face_list = [face.id for face in faces]
        print("All faces for current user: ", face_list)

    return render_template('profile.html', data=face_list, appends=2-len(face_list))

@profile.route('/upload')
def profile_page():
    return render_template('face_image.html')

@profile.route('/query/<path:indvId>')
def query_face(indvId):
    indvPhoto = IndvPhoto.query.get(indvId)

    file_name = indvPhoto.file_name
    file_path = os.path.join(path.parent.parent, indvPhoto.file_path)

    return send_from_directory(file_path, file_name)

@profile.route('/delete/<path:indvId>')
def delete_face(indvId):

    result_code = 1
    result_message = ""

    try:
        #step1: delete from db
        indvPhoto = IndvPhoto.query.get(indvId)
        db.session.delete(indvPhoto)
        db.session.flush()
        print("1 --> delete individual photo [{}] from db.".format(indvId))

        #step2: delete individual face embedding
        for aa in db.session.query(FaceEmbedding).\
                            filter(FaceEmbedding.indv_photo_id == indvId).\
                            filter(FaceEmbedding.group_photo_id == None):
            print("-------", str(aa.embedding))

            db.session.delete(aa)
            db.session.flush()
        print("2 --> delete individual face embedding from db.")

        #step3: update individual id for group photos
        embeddings = FaceEmbedding.query.filter(
                    FaceEmbedding.group_photo_id != None
                ).filter(
                    FaceEmbedding.indv_photo_id == indvId
                ).all()

        if embeddings:
            print("Having group embeddings to update.")
            for bb in embeddings:
                bb.indv_photo_id = None
            db.session.flush()
            print("3 --> update individual related group embedding in db.")

        #step4: remove file from disk
        result_code = util.delete_processed_file(indvPhoto.file_name)
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
def upload_face():
    if request.method == "POST":
        try:
            username = request.form['username']
            file = request.files['faceFile']

            #step1: get face embending
            data = photos.get_embedding(file)
            print("embedding info: " + str(data))

            if data["code"] != "0":
                return jsonify({"error": data["message"]})

            #step2: save file to disk
            result = util.save_processed_file(file)
            if result == 1:
                print("file saved failed.")
                return jsonify({"error": "file uploaded failed."})
            
            #step3: save to db
            result = photos.save_IndividualPhoto(name = username, 
                                    file_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email),
                                    file_name = file.filename,
                                    uploaded_by = current_user.id,
                                    embedding = data["embedding"],
                                    bbox = data["bbox"])
            if result == 1:
                print("save info to database failed.")

                # delete uploaded file
                result = util.delete_processed_file(file.filename)
                if result == 1:
                    print("delete file failed.")

                # return error message
                return jsonify({"error": "file uploaded failed."})
            
            print('file uploaded successful.')
            return jsonify({'message': "successful"})
        except Exception as e:
            print("System Error: ", e)
            return jsonify({"error": "System Error. Please contact administrator."})

