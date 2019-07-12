"""
LoginManager config file.
"""
from flask import (redirect, url_for)
from flask_login import LoginManager

from barscreen.database import db
from barscreen.database.user import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("dashboard.login"))