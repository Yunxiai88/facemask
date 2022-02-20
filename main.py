import os
import sys
import json
import time
import pathlib
import argparse
import pandas as pd

from glob import glob
from io import BytesIO
from zipfile import ZipFile

from werkzeug.utils import secure_filename
from flask import render_template, jsonify, flash
from flask import Blueprint, Flask, request, redirect, send_file
from flask_login import login_required, current_user

from application import db, create_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

from application.util import getFiles

images = []
database = []
length = 0

main = Blueprint('main', __name__)

@main.route("/error")
def error():
    return render_template("error.html")

@main.route("/")
@login_required
def index():
    # return the rendered template
    return render_template("index.html", name=current_user.name)

@main.route("/detail")
def detail():
    #database = loadUserInfo()
    database = []
    try:
        database[0]
    except IndexError:
        return redirect("/error")

    length = len(database)

    # return the rendered template
    return render_template("detail.html", data=database, len=length)

@main.route("/filters", methods=['POST'])
def filters():
    images = []

    filterImages = request.form.get('filterImages')
    if filterImages and len(filterImages) > 0:
        images = filterImages.split(',')

    print("filters --> ", images)

    return render_template("mask.html", data=images)

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
@main.route('/upload',methods = ['POST', 'GET'])
def upload():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect("/")
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')  
            return redirect("/")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # TODO process batch file
            result = ""
            if result == "success":
                flash('file uploaded and process successful.')
            else:
                flash('file uploaded or process failed.')
            return redirect("/")
        else:
            flash('No allow file format')
            return redirect("/")

@main.route('/load', methods = ['POST', 'GET'])
@login_required
def load():
    if request.method == "POST":
        #id = request.form.get('students')
        #print("fetching images for [" + str(id) + "]")

        # Get images for selected user
        images = getFiles()
        users = [['aaaa', 'bbbbb']]
        print(images)

        #return redirect("/detail")
        return render_template("detail.html", data=images, users=users, len=length)

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