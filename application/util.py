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

def get_upload_files() :
    upload_path = current_app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_path):
        print("create a new folder")
        os.makedirs(upload_path)
    
    file_list = []
    
    for file in os.listdir(upload_path):
        file_list.append(file)
    return file_list

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(fpath, file):
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(fpath, filename))
        return 1
    return 0