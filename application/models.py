from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), primary_key=False, unique=False, nullable=False)
    name = db.Column(db.String(1000))
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp(), index=False, unique=False, nullable=True)
    last_login = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    
    # one-to-many -- individual photo
    indvPhotos = db.relationship('IndvPhoto', backref='indv_photo', lazy=True)

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
    __tablename__ = "role"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class IndvPhoto(db.Model):
    __tablename__ = "indv_photo"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    file_path = db.Column(db.String(100), unique=False, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # one-to-many
    embeddings = db.relationship('FaceEmbedding', backref='indv_photo', lazy=True)

    def __init__(self, name, file_path, uploaded_by):
        self.name = name
        self.file_path = file_path
        self.uploaded_by = uploaded_by

class GroupPhoto(db.Model):
    __tablename__ = "group_photo"

    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(100), unique=False, nullable=False)
    face_no = db.Column(db.Integer, unique=False, nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # one-to-many
    embeddings = db.relationship('FaceEmbedding', backref='group_photo', lazy=True)

    def __init__(self, file_path, face_no, uploaded_by):
        self.file_path = file_path
        self.face_no = face_no
        self.uploaded_by = uploaded_by

class FaceEmbedding(db.Model):
    __tablename__ = "face_embedding"

    id = db.Column(db.Integer, primary_key=True)
    embedding = db.Column(db.String(2000), primary_key=False)
    bbox = db.Column(db.String(500), unique=False, nullable=False)

    # foreign keys
    group_photo_id = db.Column(db.Integer, db.ForeignKey('group_photo.id'), nullable=True)
    indv_photo_id = db.Column(db.Integer, db.ForeignKey('indv_photo.id'), nullable=True)

    def __init__(self, embedding, bbox, group_photo_id, indv_photo_id):
        self.embedding = embedding
        self.bbox = bbox
        self.group_photo_id = group_photo_id
        self.indv_photo_id = indv_photo_id

class Clusters(db.Model):
    __tablename__ = "clusters"

    id = db.Column(db.Integer, primary_key=True)
    cluster_no = db.Column(db.Integer, unique=False, nullable=False)

    # foreign keys
    indv_photo_id = db.Column(db.Integer, db.ForeignKey('indv_photo.id'))
    clustering_log_id = db.Column(db.Integer, db.ForeignKey('clustering_log.id'))
    face_embedding_id = db.Column(db.Integer, db.ForeignKey('face_embedding.id'))

    def __init__(self, cluster_no, indv_photo_id, clustering_log_id, face_embedding_id):
        self.cluster_no = cluster_no
        self.indv_photo_id = indv_photo_id
        self.clustering_log_id = clustering_log_id
        self.face_embedding_id = face_embedding_id

class ClusteringLog(db.Model):
    __tablename__ = "clustering_log"

    id = db.Column(db.Integer, primary_key=True)
    group_photo_ids = db.Column(db.String(500), nullable=True)
    cluster_nos = db.Column(db.Integer, unique=False, nullable=False)
    clustered_by = db.Column(db.String(50), nullable=False)
    clustered_date = db.Column(db.Date, nullable=False)

    def __init__(self, group_photo_ids, cluster_nos, clustered_by, clustered_date):
        self.group_photo_ids = group_photo_ids
        self.cluster_nos = cluster_nos
        self.clustered_by = clustered_by
        self.clustered_date = clustered_date