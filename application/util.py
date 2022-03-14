import os
import csv
import json
from flask import current_app
from flask_login import current_user
from application import db, create_app, util
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# get all processed files
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

# create foler if not exist
def create_folder(email):
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], email)
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

# get all uploaded file
def get_upload_files() :
    upload_path = current_app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_path):
        print("create a new folder")
        os.makedirs(upload_path)
    
    file_list = []
    
    for file in os.listdir(upload_path):
        file_list.append(file)
    return file_list

# validate image file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# save common file
def save_file(fpath, file):
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(fpath, filename))
        return 0
    return 1

# save processed file
def save_processed_file(file):
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email)

    file.stream.seek(0)

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(processed_path, filename))
        return 0
    return 1

# delete processed file
def delete_processed_file(filename):
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], current_user.email)

    delete_file = os.path.join(processed_path, filename)

    try:
        if os.path.isfile(delete_file):

            os.unlink(delete_file)

            # log file
            print(filename + " been removed.")
            return 0
        else:
            print(filename + " not exist.")
            return 1
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (delete_file, e))
        return 1