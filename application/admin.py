import os
import pathlib

from . import db
from application import photos, util, face_model
from .models import GroupPhoto, FaceEmbedding
from asyncio.windows_events import NULL

from flask import Blueprint, jsonify, request, flash
from flask import render_template, current_app, send_from_directory, url_for, redirect
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')

path = pathlib.Path(__file__)

@admin.route("/upload")
@login_required
def upload():
    return render_template("admin.html")

@admin.route('/cluster', methods=['GET'])
@login_required
def cluster_faces():
    if current_user.has_role('admin'):
        # start clustering
        res_cluster = face_model.clustering_group_photos(current_user.id)
        if res_cluster==1:
            # return error message
            return jsonify({"error": "Clustering failed."})

        return jsonify({'message': "successful"})
    else:
        return jsonify({"error": "You dont have right to execute this function."})

@admin.route('/upload', methods = ['POST'])
@login_required
def upload_post():
    filepaths = []
    save_path = current_app.config['UPLOAD_FOLDER_GRP']

    try:
        #step1: check role
        if not current_user.has_role('admin'):
            raise Exception("You dont have right to execute this function.")

        #step2: save to disk
        files = request.files.getlist("files")
        for file in files:
            result = util.save_file(save_path, file)
            if result == 1:
                raise Exception("save file for: {0} failed.".format(file.filename))
            filepaths.append(os.path.join(save_path, file.filename))
        print("save file to disk successful.")

        #step3: save to DB
        res_data = photos.save_GroupPhotos(filepaths, current_user.id)
        if res_data == 1:
            raise Exception("save info to database failed.")
        else:
            print("save info to database successful.")

        #step4: trigger cluster
        res_cluster = face_model.clustering_group_photos(current_user.id)
        if res_cluster == 1:
            raise Exception("Clustering failed.")
        else:
            print("Clustering successful.")
        
        db.session.commit()
        print('uploading batch photos successful.')
    except Exception as e:
        print("System Error: ", e)

        #rollback: delete uploaded file
        res_data = util.delete_group_files(filepaths)
        if res_data == 1:
            print("delete files failed.")
        
        #rollback: delete
        
        # return error message
        return jsonify({"error": "file uploaded failed."})
    
    return jsonify({'message': "successful"})

@admin.route("/delete", methods=['POST'])
@login_required
def delete():
    grp_photos = []

    try:
        delete_images = request.form.get('deleteImages')

        if delete_images and len(delete_images) > 0:
            grp_photo_ids = delete_images.split(',')
            print("deleting group photos {0}".format(grp_photo_ids))

            #step1: delete from db
            for grp_photo_id in grp_photo_ids:
                group_photo = photos.get_grp_photo(grp_photo_id)

                result = photos.delete_grp_photo([grp_photo_id])
                if result == 1:
                    raise Exception('delete group photo record from db failed')

                grp_photos.append(group_photo)
                
            #step2: delete from disk
            for photo in grp_photos:
                file_name, file_path  = util.get_file_name_from_path(photo.file_path)

                print("delete image --> ", file_name)
                os.remove(os.path.join(file_path, file_name))

            # confirm transaction
            db.session.commit()

            result_message = "Delete individual photo successful."
            print(result_message)
    except Exception as e:
        print(e)
        result_message = "delete photo failed, Please contact administrator"
    
    flash(result_message)

    return redirect(url_for("admin.view"))

@admin.route("/view")
@login_required
def view():
    photo_ids = []

    # fetch all group photo for admin
    group_photos = current_user.uploaded_group_photos
    if group_photos:
        for photo in group_photos:
            photo_ids.append(photo.id)
            images = os.path.split(photo.file_path)[1]
        print(images)

    return render_template("view.html", data=photo_ids)

@admin.route('/query/<path:photoId>')
def query_file(photoId):
    photo = photos.get_grp_photo(photoId)

    file_name, file_path  = util.get_file_name_from_path(photo.file_path)
    upload_path = os.path.join(path.parent.parent, file_path)

    return send_from_directory(upload_path, file_name)