from flask import (render_template, abort, json, request, flash, jsonify)
from flask_login import login_required
import logging
import re

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.loop import Loop
from barscreen.database.promo import Promo
from barscreen.database.show import Show
from barscreen.database.user import User
from barscreen.forms.loop import (NewLoopForm, UpdateLoopForm)
from barscreen.services.google_clients import GoogleStorage


@admin.route("/user/<user_id>/loops/new", methods=["GET", "POST"])
@login_required
@requires_admin
def add_loop(user_id):
    # Pull user to create loop for.
    current_user = db.session.query(User).filter(
        User.id == user_id
    ).first()

    # Initialize form.
    form = NewLoopForm()

    # Handle new loop creation.
    if request.method == "POST" and form.validate_on_submit():
        
        # Save image file locally.
        uploaded_file = form.save_uploaded_file()

        # Ensure file saved successfully.
        if not uploaded_file:
            flash("Error uploading loop, please try again.", category="error")
            abort(400)
        
        # Attempt to upload image to GoogleStorage.
        try:
            # Initialize google storage client.
            storage = GoogleStorage()
            
            # Upload image to correct bucket.
            image_url = storage.upload_file(uploaded_file, bucket="loop_images")

            # Get play list from form.
            playlist_data = json.loads(form.loop_data.data).get("data")

            # Append new loop to current user.
            current_user.loops.append(Loop(
                name=form.loop_name.data,
                image_url=image_url,
                playlist=playlist_data
            ))
            db.session.commit()
            flash("Successfully created new loop.", category="success")
            
        except Exception as err:
            logging.error("Error uploading loop for user {}: {} {}".format(current_user.id, type(err), err))
            flash("Error uploading loop, please try again.")
            abort(400)

    # Get all available Shows and Promos for current user. 
    shows = Show.query.all()
    promos = Promo.query.filter_by(user_id=user_id).all()
    return render_template("admin/add_loop.html", current_user=current_user, shows=shows, promos=promos, form=form)


@admin.route("/user/<user_id>/loops/<loop_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def edit_loop(user_id, loop_id):
    """
    Edit existing loop route.
    """
    # Pull loop and user from route data.
    current_loop = db.session.query(Loop).filter(
        Loop.id == loop_id
    ).first()
    current_user = db.session.query(User).filter(
        User.id == user_id
    ).first()
    
    # Return 404 if either aren't found.
    if not all([current_loop, current_user]):
        abort(404)
    
    # Initialize form.
    form = UpdateLoopForm()

    # Handle loop update post requests.
    if request.method == "POST" and form.validate_on_submit():

        ## Check existing loop attributes vs posted ones to see what we need to update.
        # Check playlist, if none posted for some reason, use the existing one as the "new value".
        loop_playlist = json.loads(form.loop_data.data).get("data", current_loop.playlist)
        print(loop_playlist, current_loop.playlist)
        if current_loop.playlist != loop_playlist:
            current_loop.playlist = loop_playlist

        # Check loop name.        
        if current_loop.name != form.loop_name.data:
            current_loop.name = form.loop_name.data
        
        # Check for a newly uploaded image.
        if form.loop_image.data:
            uploaded_file = form.save_uploaded_file()
            error = False
            if not uploaded_file:
                error = True
            else:
                # Attempt to upload new image        
                try:
                    # Initialize GoogleStorag        
                    storage = GoogleStorage()        

                    # Upload image.
                    image_url = storage.upload_file(uploaded_file, "loop_images")
                except Exception as err:
                    error = True
            # If error, let the user know. Otherwise compare image_url vs existing one.
            if error:
                flash("Error updating loop image, please try again.", category="error")
            else:
                if current_loop.image_url != image_url:
                    print("Updated image_url")
                    current_loop.image_url = image_url
        
        # Commit any changes to the db.
        db.session.commit()

    # Pull all shows and promos.
    shows = db.session.query(Show).all()        
    promos = db.session.query(Promo).filter(
        Promo.user_id == user_id
    ).all()

    # Get loop playlist in the correct format the front end needs.
    loop_playlist = []

    # Iterate each item in the loop's playlist.
    for i in current_loop.playlist:

        # Strips the id out of the name.
        media_id = re.search(r'\d+', i).group()
    
        # Add promo if current i is promo/
        if 'promo' in i.lower():
            promo = db.session.query(Promo).filter(
                Promo.id == media_id).first()
            if not promo:
                continue
            loop_playlist.append(
                {'id': promo.id, 'name': promo.name, 'image_url': promo.image_url, 'type': 'promo'})
     
        # Add show if current i is show.
        else:
            show = Show.query.filter_by(id=media_id).first()
            loop_playlist.append({'id': show.id, 'name': show.name,
                                  'image_url': show.clips[-1].image_url, 'type': 'show'})
    return render_template("admin/edit_loop.html", loop_playlist=json.dumps(loop_playlist), current_loop=current_loop, current_user=current_user, shows=shows, promos=promos, form=form)

