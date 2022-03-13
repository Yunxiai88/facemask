import os
import csv
import json
from flask import current_app
from flask_login import current_user
from application import db, create_app, util
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def get_file(email) :
    file_list = []
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], email)

    if not os.path.exists(processed_path):
        print("folder for this user not exists")
    else:
        count = 0
        for file in os.listdir(processed_path):
            # fetch max two images
            if count >= 2:
                break
            
            file_list.append(file)
            count += 1
    return file_list

def create_folder(email):
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], email)
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

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
        return 0
    return 1

def save_processed_file(file):
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email)

    file.stream.seek(0)

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(processed_path, filename))
        return 0
    return 1