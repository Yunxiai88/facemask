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
    uploaded_indv_photos = db.relationship('IndividualPhoto', backref='user', lazy=True)
    uploaded_group_photos = db.relationship('GroupPhoto', backref='admin', lazy=True)
    clustering_log = db.relationship('ClusteringLog', backref='admin', lazy=True)

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



class IndividualPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    filepath = db.Column(db.String(100), unique=False, nullable=False)
    embedding = db.Column(db.String(2000), nullable=True)
    face_bbox = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)
    deleted_at = db.Column(db.DateTime(), nullable=True)

    # one-to-many
    face_embedding = db.relationship('FaceEmbedding', backref='indv_photo', lazy=True)
    cluster = db.relationship('Cluster', backref='indv_photo', lazy=True)

    def __init__(self, name, filepath, embedding, face_bbox, user_id, created_at, updated_at, deleted_at):
        self.name = name
        self.filepath = filepath
        self.embedding = embedding
        self.face_bbox = face_bbox
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at


class GroupPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(100), unique=False, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    no_of_faces = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)
    deleted_at = db.Column(db.DateTime(), nullable=True)

    # one-to-many
    face_embedding = db.relationship('FaceEmbedding', backref='grp_photo', lazy=True)
    clustering_log = db.relationship('ClusteringLog', backref='grp_photo', lazy=True)

    def __init__(self, name, filepath, embedding, face_bbox, user_id, created_at, updated_at, deleted_at):
        self.name = name
        self.filepath = filepath
        self.embedding = embedding
        self.face_bbox = face_bbox
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

class FaceEmbedding(db.Model):
    __tablename__ = "face_embedding"

    id = db.Column(db.Integer, primary_key=True)
    embedding = db.Column(db.String(2000), primary_key=False)
    face_bbox = db.Column(db.String, nullable=True)
    indv_id = db.Column(db.Integer, db.ForeignKey('individual_photo.id'))
    grp_photo_id = db.Column(db.Integer, db.ForeignKey('group_photo.id'), nullable=False)

    # one-to-many
    cluster = db.relationship('Cluster', backref='face_embedding', lazy=True)

    def __init__(self, embedding, user_id):
        self.embedding = embedding
        self.user_id = user_id

class ClusteringLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grp_photo_ids = db.Column(db.String, db.ForeignKey('group_photo.id'), nullable=False)
    no_of_clusters = db.Column(db.Integer, nullable=True)
    clustered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    clustered_at = db.Column(db.DateTime(), nullable=False)

    # one-to-many
    cluster = db.relationship('Cluster', backref='clustering_log', lazy=True)

class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    face_embedding_id = db.Column(db.Integer, db.ForeignKey('face_embedding.id'), nullable=False)
    cluster_no = db.Column(db.Integer, nullable=False)
    clustering_log_id = db.Column(db.Integer, db.ForeignKey('clustering_log.id'), nullable=False)
    pred_indv_id = db.Column(db.Integer, db.ForeignKey('indvidual_photo.id'), nullable=False)

