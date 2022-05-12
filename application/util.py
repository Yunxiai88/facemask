import os
import cv2
import csv
import json
import uuid
import numpy as np

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
    upload_path = current_app.config['UPLOAD_FOLDER_INDV']

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
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    file.stream.seek(0)

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(fpath, filename))
        return 0
    return 1

# delete processed file
def delete_file(filepath, filename):
    try:
        delete_file = os.path.join(filepath, filename)

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

# delete group files
def delete_group_files(filenames):
    try:
        for filename in filenames:
            if os.path.isfile(filename):

                os.unlink(filename)

                # log file
                print(filename + " been removed.")
                
            else:
                print(filename + " not exist.")
                return 1

        return 0

    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (filename, e))
        return 1

def delete_list_by_index(lst, idx):
    return [j for i, j in enumerate(lst) if i not in idx]

def get_file_name_from_path(file_path):
    file_name = file_path.split('\\')[-1]
    file_path = file_path.replace(file_name, '')
    return file_name, file_path

def get_unique_name():
    return "{0}.{1}".format(uuid.uuid4(), 'png')

def convert_embedding(embedding):
    embedding = [float(j) for j in embedding[1:-1].split()]
    return np.array(embedding)

def convert_bbox(face_bbox):
    face_bbox = [int(j) for j in face_bbox[1:-1].split(', ')]
    return face_bbox

def get_mask(original_image, mask_image, top, right, bottom, left):
    ones = np.ones((original_image.shape[0], original_image.shape[1]))*255
    alpha_original_image = np.dstack([original_image, ones])

    resized_mask_image = cv2.resize(mask_image, (right - left, bottom - top))

    alpha_mask_image = resized_mask_image[:, :, 3] / 255.0
    alpha_mask_image_1 = 1 - alpha_mask_image

    for c in range(0, 3): 
        original_image[top:bottom, left:right, c] = ((alpha_mask_image_1 * alpha_original_image[top:bottom, left:right, c]) + (alpha_mask_image * resized_mask_image[:, :, c]))
    
    return original_image