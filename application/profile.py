import os
from .models import IndvPhoto

from application import util, users, photos

from flask_login import current_user

from flask import Blueprint, jsonify, current_app, session
from flask import render_template, request, redirect, url_for, send_from_directory

profile = Blueprint('profile', __name__, url_prefix='/profile')

@profile.route('/')
def walk_face():
    faces = current_user.indvPhotos

    face_list = []

    if faces:
        face_list = [face.id for face in faces]
        print("All faces for current user: ", face_list)

    return render_template('profile.html', data=face_list, appends=2-len(face_list))

@profile.route('/upload')
def upload_page():
    return render_template('face_image.html')

@profile.route('/faces/<path:indvId>')
def query_face(indvId):
    indvPhoto = IndvPhoto.query.get(indvId)

    file_path = indvPhoto.file_path
    file_name = indvPhoto.file_name
    print("file path: " + file_path, " file name: " + file_name)

    return send_from_directory(file_path, file_name)

@profile.route('/faces/<path:indvId>')
def delete_face(indvId):
    indvPhoto = IndvPhoto.query.get(indvId)

    db.session.delete(indvPhoto)
    db.session.commit()

    return redirect(url_for("admin.view"))

@profile.route('/faces/upload',methods = ['POST'])
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
            print(e)
            return jsonify({"error": "System Error. Please contact administrator."})

