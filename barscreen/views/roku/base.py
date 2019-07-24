from binascii import hexlify
from flask import (request, abort, jsonify)
from os import urandom
import random
import re

from . import roku
from barscreen.database import db
from barscreen.database.user import User


@roku.route("/login", methods=["POST"])
def login():
    """
    Login route for Roku API requests.
    """
    # Verify we have required post data.
    req = request.get_json()
    if not req:
        abort(400, "Post data can not be empty.")
    if not req.get("email") or not req.get("password"):
        abort(400, "Missing fields. Post data must include an email and password field.")

    # Try and match user off given email.
    matched_user = db.session.query(User).filter(
        User.email == req["email"]).first()

    # Ensure we actually have a matched user.
    if not matched_user:
        abort(401, "invalid credentials")

    # Verify password matches hash.
    if not matched_user.check_password(req["password"]):
        abort(401, "invalid credentials")

    # If user doesn't already have an api key, generate one.
    if not matched_user.api_key:
        matched_user.api_key = hexlify(urandom(32))
        db.session.commit()

    return jsonify({"status": "success", "api_key": matched_user.api_key})
