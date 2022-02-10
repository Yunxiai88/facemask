from flask import render_template
from flask import Blueprint, redirect
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    # if the above check passes, then we know the user has the right credentials
    #login_user(user, remember=remember)
    return render_template("index.html")

@auth.route('/signup')
def signup():
    return render_template('register.html')

@auth.route('/logout')
def logout():
    logout_user()
    return render_template('index.html')
