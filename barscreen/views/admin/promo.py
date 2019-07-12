from flask import (abort, render_template, redirect, request, flash)
from flask_login import login_required
import logging
from werkzeug.utils import secure_filename

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.promo import Promo
from barscreen.database.user import User
from barscreen.forms.new_promo import NewPromoForm
from barscreen.services.google_clients import GoogleStorage
from barscreen.services.imaging import screencap_from_video

@admin.route("/user/<user_id>/promos/<promo_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def promo(user_id, promo_id):
    """ Specific channel route, allows edits to specified channel. """
    current_promo = db.session.query(Promo).filter(
        Promo.user_id == user_id,
        Promo.id == promo_id,
    ).first()
    if not current_promo:
        abort(404, {"error": "No promo by that id. (id:{})".format(promo_id)})
    return render_template("admin/promo.html", current_promo=current_promo, user_id=user_id)


@admin.route("/user/<user_id>/promos/new", methods=["POST", "GET"])
@login_required
@requires_admin
def add_promo(user_id):
    """ Add Promo route. Adds clip to whatever the current show that is being edited. """
    # Get current user that the promo is being added to.
    current_user = db.session.query(User).filter(
        User.id == user_id
    ).first()

    # Ensure user exists.
    if not current_user:
        flash("User not found.", category="error")
        abort(404)
        
    form = NewPromoForm()

    # On POST, handle new promo creation.
    if request.method == "POST" and form.validate_on_submit():

        # Save file locally.
        uploaded_file = form.save_uploaded_file()

        # Get screencap from uploaded video.
        screencap = screencap_from_video(uploaded_file)

        # If we don't have both the uploaded file and the screencap, error out.
        if not all([uploaded_file, screencap]):
            flash("Error uploading promo.", category="error")
            abort(400)

        # Try to upload both files to GoogleStorage.
        try:
            # Initialize GoogleStorage client.
            storage = GoogleStorage()

            # Upload screencap.
            screencap_url = storage.upload_file(screencap, bucket="promo_images")

            # Upload video.
            video_file = storage.upload_file(uploaded_file, bucket="promo_videos")

            # Create new Promo object and add it to current user.
            current_user.promos.append(Promo(
                name=form.promo_name.data,
                description=form.description.data,
                clip_url=video_file,
                image_url=screencap_url,
            ))
            db.session.commit()

        except Exception as err:
            logging.error("Error uploading promo to user {}: {}, {}".format(current_user.id, type(err), err))
            flash("Error creating promo, please try again.", category="error")
            abort(400)

        flash("Promo created successfully.", category="success")
    return render_template("admin/add_promo.html", form=form, current_user=current_user)