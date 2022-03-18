import os
import pathlib

from . import db
from application import photos, util, face_recognition
from .models import GroupPhoto, FaceEmbedding
from asyncio.windows_events import NULL

from flask import Blueprint, jsonify, request
from flask import render_template, current_app, send_from_directory, url_for, redirect
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')

path = pathlib.Path(__file__)

@admin.route("/upload")
@login_required
def upload():
    return render_template("admin.html")

@admin.route('/upload', methods = ['POST'])
@login_required
def upload_post():
    if request.method == "POST":
        isOk = True
        filepaths = []

        save_path = current_app.config['UPLOAD_FOLDER_GRP']

        files = request.files.getlist("files")
        for file in files:
            result = util.save_file(save_path, file)
            if result == 1:
                isOk = False
                break
            filepaths.append(os.path.join(save_path, file.filename))

        if isOk:
            result = photos.save_GroupPhotos(filepaths, current_user.id)
            if result == 1:
                print("save info to database failed.")
                
                # delete uploaded file
                result = util.delete_group_files(filepaths)
                if result == 1:
                    print("delete files failed.")

                # return error message
                return jsonify({"error": "file uploaded failed."})
            
            print('file uploaded successful.')
            
        else:
            print('file uploaded failed.')
            return jsonify({"error": "file uploaded failed."})
        
        return jsonify({'message': "successful"})

@admin.route("/delete", methods=['POST'])
@login_required
def delete():
    images = []

    save_path = current_app.config['UPLOAD_FOLDER_GRP']

    #step1: delete from db

    #step2: delete from disk
    deleteImages = request.form.get('deleteImages')
    if deleteImages and len(deleteImages) > 0:
        images = deleteImages.split(',')

    for image in images:
        print("delete image --> ", image)
        os.remove(os.path.join(save_path, image))

    return redirect(url_for("admin.view"))

@admin.route("/view")
@login_required
def view():
    images = []

    # fetch all group photo for admin
    group_photos = current_user.uploaded_group_photos

    if group_photos:
        images = [photo.file_name for photo in group_photos]
        print(images)

    return render_template("view.html", data=group_photos)

@admin.route('/uploads/<path:filename>')
def download_file(filename):
    config_path = current_app.config['UPLOAD_FOLDER_GRP']
    upload_path = os.path.join(path.parent.parent, config_path)

    return send_from_directory(upload_path, filename)