import os
import pathlib
from application import util
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
def upload_post():
    if request.method == "POST":
        isOk = True
        save_path = current_app.config['UPLOAD_FOLDER']

        files = request.files.getlist("files")
        for file in files:
            result = util.save_file(save_path, file)
            if result == 0:
                isOk = False
                break
        
        if isOk:
            print('file uploaded successful.')
        else:
            print('file uploaded failed.')
        
        return jsonify({'message': "successful"})

@admin.route("/delete", methods=['POST'])
def process():
    images = []

    deleteImages = request.form.get('deleteImages')
    if deleteImages and len(deleteImages) > 0:
        images = deleteImages.split(',')

    save_path = current_app.config['UPLOAD_FOLDER']
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
    upload_path = os.path.join(path.parent.parent, current_app.config['UPLOAD_FOLDER'])

    return send_from_directory(upload_path, filename)