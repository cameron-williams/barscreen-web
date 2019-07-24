"""
Authentication helpers/functions.
"""

import binascii
from flask import (flash, redirect, url_for)
from flask_login import current_user
from functools import wraps
import hashlib
from itsdangerous import URLSafeTimedSerializer, URLSafeSerializer
import os

from barscreen.config.env import (SECRET_KEY, SECURITY_PASSWORD_SALT)


class InvalidTokenError(Exception):
    pass


def requires_admin(f):
    """
    Route decorator. User must be admin to access.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.admin:
            flash("Invalid user permissions.")
            return redirect(url_for("dashboard.login"))
        return f(*args, **kwargs)
    return wrapper


def generate_token(email, expires=True):
    """
    Generates a mutli-use token, can specify if it expires or not.
    """
    if expires:
        serializer = URLSafeTimedSerializer(SECRET_KEY)
    else:
        serializer = URLSafeSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    """
    Confirms given token. Will return the value
    of it if successful, otherwise raises InvalidTokenError.
    """
    try:
        if expiration:
            serializer = URLSafeTimedSerializer(SECRET_KEY)
            email = serializer.loads(
                token,
                salt=SECURITY_PASSWORD_SALT,
                max_age=expiration
            )
        else:
            serializer = URLSafeSerializer(SECRET_KEY)
            email = serializer.loads(
                token,
                salt=SECURITY_PASSWORD_SALT
            )
    except Exception:
        raise InvalidTokenError
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
