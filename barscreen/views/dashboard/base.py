from flask import (render_template, request, redirect,
                   flash, url_for, abort, jsonify)
from flask_login import (login_required, login_user, logout_user, current_user)
from werkzeug.utils import secure_filename

from . import dashboard
from barscreen.auth import (verify_password, generate_token, confirm_token, InvalidTokenError)
from barscreen.database import db
from barscreen.database.promo import Promo
from barscreen.database.user import User
from barscreen.forms.login import LoginForm
from barscreen.forms.account import CreatePassword
from barscreen.forms.new_promo import NewPromoForm
from barscreen.services.google_clients import Gmail, GoogleStorage


@dashboard.route("/")
@login_required
def index():
    return render_template("dashboard/dashboard.html")


@dashboard.route("/index")
@login_required
def alt_index():
    return render_template("dashboard/dashboard.html")


@dashboard.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dashboard.login'))


@dashboard.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        
        # Try and match user off given email.
        matched_user = db.session.query(User).filter(User.email==form.email.data).first()

        # Ensure we have a matched user on email.
        if matched_user:
        
            # Double check password matches hash.
            if matched_user.check_password(str(form.password.data)):
                login_user(matched_user)
                if matched_user.admin:
                    return redirect(url_for("admin.index"))
                return redirect(url_for("dashboard.index"))

        # Flash error.
        flash("Invalid email or password.", "error")

    return render_template("dashboard/login.html", form=form)


@dashboard.route("/addpromo", methods=["POST", "GET"])
@login_required
def addpromo():
    """
    Add Promo route. Adds clip to whatever the current show that is being edited.
    """
    error = None
    form = NewPromoForm()
    if request.method == "POST" and form.validate_on_submit():
        storage = GoogleStorage()
        try:
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
        except Exception as e:
            db.session.rollback()
            if 'duplicate key value violates unique constraint' in str(e):
                error = 'show name already registered.'
        flash("Promo Created.", category="success")
    return render_template("dashboard/add_promo.html", form=form, error=error, current_user=current_user)
