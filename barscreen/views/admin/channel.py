from flask import (render_template, abort, request, flash)
from flask_login import login_required
import logging
from werkzeug.utils import secure_filename

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.channel import Channel
from barscreen.forms.new_channel import NewChannelForm
from barscreen.services.google_clients import GoogleStorage
from barscreen.services.imaging import get_image_size, resize_image

@admin.route("/channels")
@login_required
@requires_admin
def channels():
    """
    Route for viewing all channels.
    """
    channels = db.session.query(Channel).all()
    return render_template("admin/channels.html", channels=channels)


@admin.route("/channels/<channel_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def channel(channel_id):
    """
    Specific channel route.
    """
    current_channel = db.session.query(Channel).filter(
        Channel.id == channel_id
    ).first()
    if not current_channel:
        abort(404, {"error": "No channel by that id. (id:{})".format(channel_id)})
    return render_template("admin/channel.html", current_channel=current_channel)


@admin.route("/channels/create", methods=["POST", "GET"])
@login_required
@requires_admin
def add_channel():
    """
    Channel creation route
    """
    form = NewChannelForm()
    
    # Handle post (actual channel creation).
    if request.method == "POST" and form.validate_on_submit():
        
        # Complete file upload by saving the file locally.
        uploaded_file = form.save_uploaded_file()

        # Ensure the file was uploaded successfully.
        if not uploaded_file:
            flash("Error processing your upload. Please try again.")
            abort(400)

        # Check if uploaded image meets required image dimensions. If it
        # does not, then resize it.
        if get_image_size(uploaded_file) != (512, 288):
            resize_image(uploaded_file)

        # Attempt google storage upload.
        try:
            # Initialize storage client.
            storage = GoogleStorage()

            # Try and upload file.
            url = storage.upload_file(uploaded_file, bucket="channel_images")

            # Create the new Channel object to be put into the db.
            channel = Channel(
                name=form.channel_name.data,
                category=form.category.data,
                description=form.description.data,
                image_url=url
            )
            db.session.add(channel)
            db.session.commit()
            flash("Successfully completed.", category="success")

        except Exception as err:
            logging.error("Ran into an error creating a new channel: {} {} ".format(type(err), err))
            flash("Error uploading Channel. Please try again.", category="error")

    return render_template("admin/add_channel.html", form=form)
