import os
import sys
import json
import time
import pathlib
import argparse

from glob import glob
from io import BytesIO
from zipfile import ZipFile

from flask_login import login_required, current_user
from flask import Blueprint, Flask, current_app
from flask import redirect, url_for, render_template, request, send_file, send_from_directory

from application import db, create_app, util, face_model

path = pathlib.Path(__file__)
main = Blueprint('main', __name__)

#---------------------------------------------------------------------
#----------------------------Functions--------------------------------
#---------------------------------------------------------------------
@main.route("/error")
def error():
    return render_template("error.html")

@main.route("/")
@login_required
def index():
    # check whether face embedding existing in db
    if current_user.uploaded_indv_photos:

        face_list = [face.id for face in current_user.uploaded_indv_photos]
        print("individual photo ids: ", face_list)

        # return to index template
        return render_template("index.html", data=face_list)
    else:
        # return to face image template
        return redirect(url_for("profile.walk_face"))

@main.route("/process", methods=['POST'])
def process():
    indv_ids = []

    indv_photos = request.form.get('faceImages')
    if indv_photos and len(indv_photos) > 0:
        indv_ids = indv_photos.split(',')
        print("individual person id --> ", indv_ids)

        # apply face image to mask group images
        group_photos = face_model.mark_face(indv_ids)

    return render_template("process.html", data=group_photos)

@main.route("/query/<path:photoName>")
def processed_photo(photoName):
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email)
    file_path = os.path.join(path.parent, processed_path)
    return send_from_directory(file_path, photoName)

@main.route("/download", methods=['POST'])
def download():
    images = []
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email)

    selectedImages = request.form.get('selectedImages')
    images = selectedImages.split(',')

    print("download --> ", images)

    stream = BytesIO()
    with ZipFile(stream, 'w') as zf:
        for f in images:

            file = os.path.join(processed_path, f)
            print('  add: ', os.path.basename(file))
            zf.write(file, os.path.basename(file))
    stream.seek(0)

    return send_file(stream, as_attachment=True, attachment_filename='archive.zip')

#---------------------------------------------------------------------
#-------------------------Execute Function----------------------------
#---------------------------------------------------------------------
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="ip address")
    ap.add_argument("-o", "--port", type=int, default=8000, help="port number of the server")
    args = vars(ap.parse_args())

    # start the flask app
    app = create_app()
    app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)