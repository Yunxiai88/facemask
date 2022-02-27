from . import db
from .models import User, Role, UserRoles
from .models import FaceEmbedding

def get_all_user():
    return User.query.all()

def get_user_byid(user_id):
    return User.query.get(user_id)

def get_user_byemail(email):
    return User.query.filter_by(email = email).first()

def save_user(user):
    db.session.add(user)
    db.session.commit()

def save_faceEmbedding(embedding, user_id):
    faceEmbedding = FaceEmbedding(embedding, user_id)
    db.session.add(faceEmbedding)
    db.session.commit()