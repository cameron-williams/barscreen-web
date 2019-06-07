from flask import (abort, render_template, redirect, request, flash)
from flask_login import login_required
from werkzeug.utils import secure_filename

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.promo import Promo
from barscreen.database.user import User
from barscreen.forms.newpromo import NewPromoForm
from barscreen.services.google_clients import GoogleStorage


@admin.route("/user/<user_id>/<promo_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def promoid(user_id, promo_id):
    """ Specific channel route, allows edits to specified channel. """
    current_promo = db.session.query(Promo).filter(
        Promo.user_id == user_id,
        Promo.id == promo_id,
    ).first()
    if not current_promo:
        abort(404, {"error": "No promo by that id. (id:{})".format(promo_id)})
    return render_template("admin/promoid.html", current_promo=current_promo, user_id=user_id)


@admin.route("/user/<user_id>/addpromo", methods=["POST", "GET"])
@login_required
@requires_admin
def addpromo(user_id):
    """ Add Promo route. Adds clip to whatever the current show that is being edited. """
    error = None
    current_user = db.session.query(User).filter(
        User.id == user_id
    ).first()
    form = NewPromoForm()
    if request.method == "POST" and form.validate_on_submit():

        storage = GoogleStorage()
        fn = secure_filename(form.clip_file.data.filename)
        url = storage.upload_promo_video(name=fn, file=form.clip_file.data)

        # save vid and get still from it
        form.clip_file.data.save('/tmp/{}'.format(fn))
        still_img_path = ""
        # still_img_path = get_still_from_video_file(
        #     "/tmp/{}".format(fn), 5, output="/var/tmp/{}".format(fn.replace(".mp4", ".png")))
        still_url = storage.upload_promo_image(
            name=still_img_path.split("/")[-1], image_data=open(still_img_path).read())

        current_user.promos.append(Promo(
            name=form.promo_name.data,
            description=form.description.data,
            clip_url=url,
            image_url=still_url,
        ))

        db.session.commit()
        flash("Promo Created.", category="success")
    return render_template("admin/addpromo.html", form=form, error=error, current_user=current_user)