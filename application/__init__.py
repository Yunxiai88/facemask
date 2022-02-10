import sys
import pathlib
from flask import Flask

def create_app():
    # initialize a flask object
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "facemasksystemkey"
    app.config['UPLOAD_FOLDER'] = 'input'
    app.config['SESSION_TYPE'] = 'filesystem'

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app