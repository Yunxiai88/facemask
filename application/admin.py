from asyncio.windows_events import NULL
import os
import pathlib
from application import util
from .models import GroupPhoto
from . import db
from flask import Blueprint, jsonify, request
from flask import render_template, current_app, send_from_directory, url_for, redirect
from flask_login import login_required, current_user
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

path = pathlib.Path(__file__)

@admin.route("/upload")
@login_required
def upload():
    return render_template("admin.html")

@admin.route('/upload', methods = ['POST'])
def upload_post():
    if request.method == "POST":
        isOk = True
        save_path = current_app.config['UPLOAD_FOLDER_GRP']

        files = request.files.getlist("files")
        filepaths = []
        for file in files:
            result = util.save_file(save_path, file)
            if result == 0:
                isOk = False
                break
            filepaths.append(result)
        # print(current_user.id)
        
        if isOk:
            for f in filepaths:
                db.session.add(GroupPhoto(f,current_user.id, None, datetime.now(), datetime.now(), None))
            db.session.commit()
            print('file uploaded successful.')
        else:
            print('file uploaded failed.')
        
        return jsonify({'message': "successful"})

@admin.route("/delete", methods=['POST'])
def delete():
    images = []
    save_path = current_app.config['UPLOAD_FOLDER_GRP']

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
    images = util.get_upload_files()
    print("view all: ", images)

    return render_template("view.html", data=images)

@admin.route('/uploads/<path:filename>')
def download_file(filename):
    config_path = current_app.config['UPLOAD_FOLDER']
    upload_path = os.path.join(path.parent.parent, config_path)

    return send_from_directory(upload_path, filename)