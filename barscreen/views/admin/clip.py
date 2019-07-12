from flask import (abort, render_template, flash, request)
from flask_login import login_required
import logging

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.clip import Clip
from barscreen.database.show import Show
from barscreen.forms.new_clip import NewClipForm
from barscreen.services.google_clients import GoogleStorage
from barscreen.services.imaging import screencap_from_video


@admin.route("/clips")
@login_required
@requires_admin
def clips():
    """
    Base clips route.
    """
    clips = Clip.query.all()
    return render_template("admin/clips.html", clips=clips)


@admin.route("/channels/<channel_id>/shows/<show_id>/clips/<clip_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def clip(channel_id, show_id, clip_id):
    """
    Single clip route. Displays the selected clip for channel/show.
    """
    current_clip = db.session.query(Clip).filter(
        Clip.show_id == show_id,
        Clip.id == clip_id
    ).first()
    if not current_clip:
        abort(404, {"error": "No clip by that id. (id:{})".format(show_id)})
    return render_template("admin/clip.html", current_clip=current_clip, show_id=show_id, channel_id=channel_id)


@admin.route("/channels/<channel_id>/shows/<show_id>/clips/new", methods=["POST", "GET"])
@login_required
@requires_admin
def add_clip(channel_id, show_id):
    """
    Add Clip route.
    Clip will be added to whatever the current show that is being edited.
    """
    form = NewClipForm()

    # POST method is the actual uploading of a new clip.
    if request.method == "POST" and form.validate_on_submit():

        # Save the uploaded file.
        uploaded_file = form.save_uploaded_file()

        # Save a screencap from the video to use as a preview image.
        screencap = screencap_from_video(uploaded_file)

        # Ensure the uploaded file and screencap were saved successfully.
        if not all([uploaded_file, screencap]):
            flash("Error uploading clip, please try again.")
            abort(400)

        # Attempt to upload the video and the screencap to google.
        try:
            # Pull show that this clip will be associated with.
            show = db.session.query(Show).filter(
                Show.channel_id == channel_id,
                Show.id == show_id
            ).first()

            # Initialize GoogleStorage client.
            storage = GoogleStorage()

            # Upload screencap to GoogleStorage.
            screencap_url = storage.upload_file(screencap, "clip_images")

            # Upload clip to GoogleStorage.
            clip_url = storage.upload_file(uploaded_file, "clip_videos")

            # Create new Clip object and add it to current show.
            show.clips.append(Clip(
                name=form.clip_name.data,
                description=form.description.data,
                clip_url=clip_url,
                image_url=screencap_url,
            ))
            db.session.commit()
        except Exception as err:
            logging.error("Error creating new clip for show {}: {} {}".format(show.id, type(err), err))
            flash("Error creating clip, please try again.", category="error")
            abort(400)
        flash("Clip created successfully.", category="success")
    return render_template("admin/add_clip.html", form=form)
