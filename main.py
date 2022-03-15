import os
import sys
import json
import time
import pathlib
import argparse

from glob import glob
from io import BytesIO
from zipfile import ZipFile

from flask import Blueprint, Flask, render_template, request, send_file
from flask_login import login_required, current_user

from application import db, create_app, util

images = []

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
        images = util.get_file(current_user.email)
        print(images)

        # return to index template
        return render_template("index.html", data=images)
    else:
        # return to face image template
        return render_template("face_image.html")

@main.route("/process", methods=['POST'])
def process():
    images = []

    faceImages = request.form.get('faceImages')
    if faceImages and len(faceImages) > 0:
        images = faceImages.split(',')

    print("face image --> ", images)

    #TODO -- apply face image to mask group images

    return render_template("process.html", data=images)

#NO USE
@main.route("/mask", methods=['POST'])
def selected():
    images = []

    processedImages = request.form.get('processedImages')
    if processedImages and len(processedImages) > 0:
        images = processedImages.split(',')
    
    print("mask --> ", images)

    return render_template("process.html", data=images)

@main.route("/download", methods=['POST'])
def download():
    images = []

    selectedImages = request.form.get('selectedImages')
    images = selectedImages.split(',')

    print("download --> ", images)

    stream = BytesIO()
    with ZipFile(stream, 'w') as zf:
        for f in images:
            file = os.path.join('application/static/processed/', f)
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