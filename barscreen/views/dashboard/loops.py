from flask import (render_template, flash, request, json, abort)
from flask_login import (login_required, current_user)
import logging
import re
from werkzeug.utils import secure_filename

from . import dashboard
from barscreen.database import db
from barscreen.database.channel import Channel
from barscreen.database.loop import Loop
from barscreen.database.promo import Promo
from barscreen.database.show import Show
from barscreen.forms.new_promo import NewPromoForm
from barscreen.forms.loop import (
    NewLoopFormDashboard, UpdateDashboardLoopForm)
from barscreen.services.google_clients import GoogleStorage
from barscreen.services.imaging import (
    b64_image_string_to_file, screencap_from_video)


@dashboard.route("/loops")
@login_required
def loops():
    """
    Base loop view route.
    """
    return render_template("dashboard/loops.html")


@dashboard.route("/loops/<loop_id>", methods=["GET", "POST"])
@login_required
def edit_loop(loop_id):
    """
    Route for editing existing loops.
    """
    # Pull loop specified in route.
    current_loop = db.session.query(Loop).filter(Loop.id == loop_id).first()
    if not current_loop:
        abort(404, {"error": "No channel by that id. (id:{})".format(loop_id)})

    # Query Channels for the 4 categories (trends, entertainment, sports, news).
    channels = db.session.query(Channel).order_by(Channel.id.desc()).all()
    channel_categories = {
        "entertainment": [],
        "sports": [],
        "news": [],
        "trends": []
    }

    # Add 10 channels to trends.
    channel_categories["trends"] = channels[:10]

    # Iterate Channels and add them to their category.
    for channel in channels:
        # Ensure current channel is the dict of categories.
        if channel.category.lower() in channel_categories:
            channel_categories[channel.category.lower()].append(channel)

    # Initialize forms.
    # Form for new promos.
    promo_form = NewPromoForm()

    # Form for editing loop.
    loop_form = UpdateDashboardLoopForm()

    # Since we have 2 possible form posts we need to have nested ifs to handle each.
    if request.method == "POST":

        # Both forms might use GoogleStorage so initialize it here.
        try:
            # Initialize GoogleStorage client.
            storage = GoogleStorage()
        except Exception as err:
            flash("Unable to complete request, please try again later.",
                  category="error")
            abort(400)

        # Handle new promo form.
        if promo_form.validate_on_submit():

            # Save uploaded file locally.
            uploaded_file = promo_form.save_uploaded_file()
            # Get screencap from uploaded file.
            screencap = screencap_from_video(uploaded_file)
            # Ensure upload and screencap were successful.
            if not all([uploaded_file, screencap]):
                flash("Error creating loop, please try again.")
                abort(400)
            # Attempt to upload to GoogleStorage.
            try:
                # Upload screencap.
                screencap_url = storage.upload_file(
                    screencap, bucket="promo_images")
                # Upload video.
                video_url = storage.upload_file(
                    uploaded_file, bucket="promo_videos")
                # Add new promo with uploaded screencap/video to current user.
                current_user.promos.append(Promo(
                    name=promo_form.promo_name.data,
                    description=promo_form.description.data,
                    clip_url=video_url,
                    image_url=screencap_url,
                ))
                db.session.commit()
                flash("Promo created successfully.", category="success")

            # Catch all exception to notify user.
            except Exception as err:
                logging.error("Error uploading promo to user {}: {} {}".format(
                    current_user.id, type(err), err))
                flash("Error creating promo, please try again.", category="error")
                abort(400)

        # Handle loop edit form.
        elif loop_form.validate_on_submit():

            # Check each form attribute vs existing loop attribute to see if we need to update anything.
            # Check loop name.
            if current_loop.name != loop_form.loop_name.data:
                current_loop.name = loop_form.loop_name.data

            # Check loop playlist, if none posted for some reason, use the existing one as the "new value".
            try:
                loop_playlist = json.loads(loop_form.loop_data.data).get(
                    "data", current_loop.playlist)
            except ValueError:
                loop_playlist = current_loop.playlist

            if current_loop.playlist != loop_playlist:
                current_loop.playlist = loop_playlist

            # Check loop image.
            if loop_form.loop_image.data:

                # Convert b64 string and save it as local image.
                uploaded_file = b64_image_string_to_file(
                    loop_form.loop_image.data, loop_form.loop_name.data)
                if not uploaded_file:
                    flash("Error updating loop, please try again.",
                          category="error")
                    abort(400)

                # Attempt to upload image to GoogleStorage, then update it on the Loop object.
                try:
                    image_url = storage.upload_file(
                        uploaded_file, bucket="loop_images")
                    current_loop.image_url = image_url
                except Exception as err:
                    logging.error("Error uploading image for loop: {}: {} {}".format(
                        current_loop.id, type(err), err))
                    flash("Error updating loop, please try again.",
                          category="error")
                    abort(400)

            # Commit any changes and notify success.
            db.session.commit()
            flash("Loop updated successfully.", category="success")

    # Get the current loop's playlist and make it the format the template expects.  todo make this into helper function
    loop_playlist = []
    for i in current_loop.playlist:
        media_id = re.search(r'\d+', i).group()
        if 'promo' in i.lower():
            promo = db.session.query(Promo).filter(
                Promo.id == media_id).first()
            # if promo
            if not promo:
                continue
            loop_playlist.append(
                {'id': promo.id, 'name': promo.name, 'image_url': promo.image_url, 'type': 'promo'})
        else:
            show = db.session.query(Show).filter(Show.id == media_id).first()
            loop_playlist.append({'id': show.id, 'name': show.name,
                                  'image_url': show.clips[-1].image_url, 'type': 'show'})
    return render_template("dashboard/edit_loop.html", form=promo_form, loop_form=loop_form, loop_playlist=json.dumps(loop_playlist), current_loop=current_loop, current_user=current_user, trends=channel_categories["trends"], entertainments=channel_categories["entertainment"], sports=channel_categories["sports"], news=channel_categories["sports"])


@dashboard.route("/loops/new", methods=["POST", "GET"])
@login_required
def add_loop():
    """
    Create loop route. (also option to create promo, perhaps make this into 2 routes?)
    """
    # Query Channels for the 4 categories (trends, entertainment, sports, news).
    channels = db.session.query(Channel).order_by(Channel.id.desc()).all()
    channel_categories = {
        "entertainment": [],
        "sports": [],
        "news": [],
        "trends": []
    }

    # Add 10 channels to trends.
    channel_categories["trends"] = channels[:10]

    # Iterate Channels and add them to their category.
    for channel in channels:
        # Ensure current channel is the dict of categories.
        if channel.category.lower() in channel_categories:
            channel_categories[channel.category.lower()].append(channel)

    # Initialize forms.

    # Promo form.
    promo_form = NewPromoForm()

    # Loop form.
    loop_form = NewLoopFormDashboard()

    # Handle form post (loop or promo create).
    if request.method == "POST":

        try:
            # Initialize GoogleStorage client.
            storage = GoogleStorage()
        except Exception as err:
            flash("Unable to complete request, please try again later.",
                  category="error")
            abort(400)

        # Handle Promo form post.
        if promo_form.validate_on_submit():

            # Save uploaded file locally.
            uploaded_file = promo_form.save_uploaded_file()
            # Get screencap from uploaded file.
            screencap = screencap_from_video(uploaded_file)
            # Ensure upload and screencap were successful.
            if not all([uploaded_file, screencap]):
                flash("Error creating loop, please try again.")
                abort(400)
            # Attempt to upload to GoogleStorage.
            try:
                # Upload screencap.
                screencap_url = storage.upload_file(
                    screencap, bucket="promo_images")
                # Upload video.
                video_url = storage.upload_file(
                    uploaded_file, bucket="promo_videos")
                # Add new promo with uploaded screencap/video to current user.
                current_user.promos.append(Promo(
                    name=promo_form.promo_name.data,
                    description=promo_form.description.data,
                    clip_url=video_url,
                    image_url=screencap_url,
                ))
                db.session.commit()
                flash("Promo created successfully.", category="success")

            # Catch all exception to notify user.
            except Exception as err:
                logging.error("Error uploading promo to user {}: {} {}".format(
                    current_user.id, type(err), err))
                flash("Error creating promo, please try again.", category="error")
                abort(400)
            

        # Handle Loop form post.
        elif loop_form.validate_on_submit():

            # Save loop_image locally from b64 form string.
            uploaded_file = b64_image_string_to_file(
                loop_form.loop_image.data, loop_form.loop_name.data)
            if not uploaded_file:
                flash("Error creating loop, please try again later.",
                      category="error")
                abort(400)

            # Attempt to upload loop image to GoogleStorage.
            try:
                image_url = storage.upload_file(
                    uploaded_file, bucket="loop_images")

                # Get playlist data from form.
                playlist_data = json.loads(
                    loop_form.loop_data.data).get("data")

                # Create new loop and add it to current user.
                current_user.loops.append(Loop(
                    name=loop_form.loop_name.data,
                    playlist=playlist_data,
                    image_url=image_url
                ))
                db.session.commit()
                flash("Successfully created new loop.", category="success")

            except Exception as err:
                logging.error("Error uploading loop for user {}: {} {}".format(
                    current_user, type(err), err))
                flash("Error creating loop, please try again later.",
                      category="error")
                abort(400)

    return render_template("dashboard/add_loop.html", form=promo_form, loop_form=loop_form, current_user=current_user, trends=channel_categories["trends"], entertainments=channel_categories["entertainment"], sports=channel_categories["sports"], news=channel_categories["news"])
