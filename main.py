import os
import sys
import json
import time
import pathlib
import argparse

from glob import glob
from io import BytesIO
from zipfile import ZipFile

from flask import Blueprint, Flask, jsonify, flash, current_app, session
from flask import render_template, request, redirect, send_file, url_for, send_from_directory
from flask_login import login_required, current_user

from application import db, create_app, util, users, face_model

images = []
database = []

main = Blueprint('main', __name__)

@main.route("/error")
def error():
    return render_template("error.html")

@main.route('/faceimage')
def face_image():
    return render_template('face_image.html')

@main.route("/")
@login_required
def index():
    # check whether face embedding existing in db
    if current_user.indvPhotos:
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
#----------------------------Functions--------------------------------
#---------------------------------------------------------------------
@main.route('/uploadFace',methods = ['POST'])
def uploadFace():
    if request.method == "POST":
        isOk = True
        face_list = []

        files = request.files.getlist("faceFile")
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email)

        for file in files:
            # get face embending
            result = face_model.get_embedding(file)
            print("embedding info: " + str(result))

            if result["code"] != "0":
                return jsonify({"error": result["message"]})
            
            # append to list
            face_list.append(result)

        # save file to disk
        for file in files:
            result = util.save_file(processed_path, file)
            if result == 0:
                isOk = False
                break
        
        if isOk:
            print('file uploaded successful.')

            # save to db
            for face in face_list:
                users.save_IndividualPhoto(name = "name", 
                                        file_path = os.path.join(processed_path, file.filename), 
                                        uploaded_by = current_user.id,
                                        embedding = face["embedding"],
                                        bbox = face["bbox"])
        else:
            print('file uploaded failed.')
        return jsonify({'message': "successful"})

# execute function
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="ip address")
    ap.add_argument("-o", "--port", type=int, default=8000, help="port number of the server")
    args = vars(ap.parse_args())

    # start the flask app
    app = create_app()
    app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)