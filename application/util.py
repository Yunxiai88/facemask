import os
import csv
import json
import pathlib
from flask import current_app
from application import db, create_app, util
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

path = pathlib.Path(__file__)

def get_file() :
    file_path = "./application/static/processed"

    file_list = []

    if not os.path.exists(file_path):
        print("folder for this user not exists")
    else:
        count = 0
        for file in os.listdir(file_path):
            # fetch max two images
            if count >= 2:
                break
            
            file_list.append(file)
            count += 1
    return file_list

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return 1
    return 0