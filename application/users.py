from . import db
from .models import User, Role, UserRoles
from .models import FaceEmbedding, IndvPhoto

def get_all_user():
    return User.query.all()

def get_user_byid(user_id):
    return User.query.get(user_id)

def get_user_byemail(email):
    return User.query.filter_by(email = email).first()

def save_user(user):
    db.session.add(user)
    db.session.commit()

def save_faceEmbedding(embedding, bbox, group_photo_id=None, indv_photo_id=None):
    faceEmbedding = FaceEmbedding(embedding, bbox, group_photo_id, indv_photo_id)
    db.session.add(faceEmbedding)
    db.session.commit()

def save_IndividualPhoto(name, file_path, uploaded_by, embedding, bbox, group_photo_id=None):
    individualPhoto = IndvPhoto(name, file_path, uploaded_by)
    db.session.add(individualPhoto)
    db.session.flush()

    faceEmbedding = FaceEmbedding(embedding, bbox, group_photo_id, individualPhoto.id)
    db.session.add(faceEmbedding)
    db.session.flush()

    db.session.commit()