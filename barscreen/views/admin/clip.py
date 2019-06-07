from flask import (abort, render_template, flash, request)
from flask_login import login_required
from werkzeug.utils import secure_filename

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.clip import Clip
from barscreen.database.show import Show
from barscreen.forms.newclip import NewClipForm
from barscreen.services.google_clients import GoogleStorage


@admin.route("/clips")
@login_required
@requires_admin
def clips():
    clips = Clip.query.all()
    return render_template("admin/clips.html", clips=clips)


@admin.route("/channels/<channel_id>/<show_id>/<clip_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def clipid(channel_id, show_id, clip_id):
    """ Specific channel route, allows edits to specified channel. """
    current_clip = db.session.query(Clip).filter(
        Clip.show_id == show_id,
        Clip.id == clip_id
    ).first()
    if not current_clip:
        abort(404, {"error": "No clip by that id. (id:{})".format(show_id)})
    return render_template("admin/clipid.html", current_clip=current_clip, show_id=show_id, channel_id=channel_id)


@admin.route("/channels/<channel_id>/<show_id>/addclip", methods=["POST", "GET"])
@login_required
@requires_admin
def addclip(channel_id, show_id):
    """ Add Clip route. Adds clip to whatever the current show that is being edited. """
    error = None
    form = NewClipForm()
    if request.method == "POST" and form.validate_on_submit():
        storage = GoogleStorage()
        try:
            current_show = db.session.query(Show).filter(
                Show.channel_id == channel_id,
                Show.id == show_id
            ).first()

            fn = secure_filename(form.clip_file.data.filename)
            # upload video to storage and save url
            url = storage.upload_clip_video(name=secure_filename(
                form.clip_file.data.filename), file=form.clip_file.data)

            # save vid and get still from it
            form.clip_file.data.save('/tmp/{}'.format(fn))
            still_img_path = ""
            # still_img_path = get_still_from_video_file(
            #     "/tmp/{}".format(fn), 5, output="/var/tmp/{}".format(fn.replace(".mp4", ".png")))
            still_url = storage.upload_clip_image(
                name=still_img_path.split("/")[-1], image_data=open(still_img_path).read())

            current_show.clips.append(Clip(
                name=form.clip_name.data,
                description=form.description.data,
                clip_url=url,
                image_url=still_url,
            ))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if 'duplicate key value violates unique constraint' in str(e):
                error = 'show name already registered.'
        flash("Clip Created.", category="success")
    return render_template("admin/addclip.html", form=form, error=error)
