from flask import (render_template, abort, request, flash)
from flask_login import login_required
from werkzeug.utils import secure_filename

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.channel import Channel
from barscreen.forms.newchannel import NewchannelForm
from barscreen.services.google_clients import GoogleStorage

@admin.route("/channels")
@login_required
@requires_admin
def channels():
    """ Route for viewing all channels """
    channels = db.session.query(Channel).all()
    return render_template("admin/channels.html", channels=channels)


@admin.route("/channels/<channel_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def channelid(channel_id):
    """ Specific channel route, allows edits to specified channel. """
    current_channel = db.session.query(Channel).filter(
        Channel.id == channel_id
    ).first()
    if not current_channel:
        abort(404, {"error": "No channel by that id. (id:{})".format(channel_id)})
    return render_template("admin/channelid.html", current_channel=current_channel)


@admin.route("/addchannel", methods=["POST", "GET"])
@login_required
@requires_admin
def addchannel():
    form = NewchannelForm()
    error = None

    if request.method == "POST" and form.validate_on_submit():
        storage = GoogleStorage()
        image_file = form.channel_img.data
        image_data = image_file.read()
        # image_bytes = BytesIO(image_data)
        # img = Image.open(image_bytes)

        # size = img.size
        # width = size[0]
        # height = size[1]
        width = 0
        height = 0

        if width != 512 and height != 288:
            error = 'invalid image size'
            print(error)
        else:
            try:
                url = storage.upload_channel_image(name=secure_filename(
                    form.channel_img.data.filename), image_data=image_data)
                channel = Channel(
                    name=form.channel_name.data,
                    category=form.category.data,
                    description=form.description.data,
                    image_url=url
                )
                db.session.add(channel)

                db.session.commit()
                flash("Successfully completed.")

            except Exception as e:
                db.session.rollback()
                if 'duplicate key value violates unique constraint' in str(e):
                    error = 'channel name already registered.'
                else:
                    error = 'failed to add channel.'

    return render_template("admin/addchannel.html", form=form, error=error)
