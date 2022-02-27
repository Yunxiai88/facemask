from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), primary_key=False, unique=False, nullable=False)
    name = db.Column(db.String(1000))
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp(), index=False, unique=False, nullable=True)
    last_login = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    
    # one-to-many
    faceEmbedding = db.relationship('FaceEmbedding', backref='user', lazy=True)

    # role
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('user', lazy='dynamic'))

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    def has_role(self, role):
        """Check user role."""
        if any(r.name==role for r in self.roles):
            return True
        else:
            return False

    def __repr__(self):
        return "<User {}>".format(self.username)

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class FaceEmbedding(db.Model):
    __tablename__ = "face_embedding"

    id = db.Column(db.Integer, primary_key=True)
    embedding = db.Column(db.String(2000), primary_key=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, embedding, user_id):
        self.embedding = embedding
        self.user_id = user_id

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), unique=False, nullable=False)
    filepath = db.Column(db.String(100), unique=False, nullable=False)

    # one-to-many
    photoEmbedding = db.relationship('PhotoEmbedding', backref='photo', lazy=True)

class PhotoEmbedding(db.Model):
    __tablename__ = "photo_embedding"

    id = db.Column(db.Integer, primary_key=True)
    embedding = db.Column(db.String(2000), primary_key=False)
    photo_id = db.Column(db.String(100), db.ForeignKey('photo.id'))

    def __init__(self, embedding, photo_id):
        self.embedding = embedding
        self.photo_id = photo_id