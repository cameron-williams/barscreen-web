"""
LoginManager configuration file, and other authentication helpers/functions.
"""
import binascii
from flask import (flash, redirect, url_for)
from flask_login import (LoginManager, login_required,
                         login_user, current_user)
from functools import wraps
import hashlib
from itsdangerous import URLSafeTimedSerializer
import os

from barscreen.database import db
from barscreen.database.user import User
from barscreen.config.env import (SECRET_KEY, SECURITY_PASSWORD_SALT)

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("dashboard.login"))


def requires_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.admin:
            flash("Invalid user permissions.")
            return redirect(url_for("dashboard.login"))
        return f(*args, **kwargs)
    return wrapper


class InvalidTokenError(Exception):
    pass


def generate_confirmation_token(email):
    """ Generates a password creation token """
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    """ Confirms given password generation token """
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except Exception:
        raise InvalidTokenError("Token is expired.")
    return email


def hash_password(password):
    """Hash a password for storing."""
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  SECRET_KEY.encode('utf-8'), 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return pwdhash.decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  SECRET_KEY.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
