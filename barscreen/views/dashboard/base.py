from flask import (render_template, request, redirect,
                   flash, url_for, abort, jsonify)
from flask_login import (login_required, login_user, logout_user, current_user)
from werkzeug.utils import secure_filename

from . import dashboard
from barscreen.auth import verify_password, generate_confirmation_token, confirm_token, InvalidTokenError
from barscreen.database import db
from barscreen.database.promo import Promo
from barscreen.database.user import User
from barscreen.forms.login import LoginForm
from barscreen.forms.password import CreatePassword
from barscreen.forms.newpromo import NewPromoForm
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
        # try and match user off given email
        matched_user = User.query.filter_by(email=form.email.data).first()
        # double check password matches hash
        if verify_password(matched_user.password, str(form.password.data)):
            login_user(matched_user)
            if matched_user.admin:
                return redirect(url_for("admin.index"))
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid email or password.", "error")
    return render_template("dashboard/login.html", form=form)


@dashboard.route("/confirm/<token>", methods=["GET", "POST"])
@login_required
def confirm_email(token):
    # make sure token is set based off what type of request we're getting
    if token:
        form = CreatePassword(token=token)
    else:
        form = CreatePassword()
    if not token:
        token = form.token.data
    # try and confirm token, abort to signup if invalid or expired
    try:
        email = confirm_token(token)
    except InvalidTokenError:
        flash('The confirmation link is invalid or has expired.', category='danger')
        return redirect(url_for('base.signup'))

    # pull user associated with token
    user = User.query.filter_by(email=email).first()
    if not user:
        abort(400, 'Invalid token.')

    # if form submit, add new password to user and redirect them to dashboard
    if request.method == "POST" and form.validate_on_submit():
        user.set_password(form.password.data)
        user.confirmed = True
        db.session.commit()
        flash("Password set successfully.", category="success")
        return redirect(url_for('dashboard.index'))
    return render_template("dashboard/password.html", form=form, token=token)


@dashboard.route("/change_password", methods=["POST"])
def change_password():
    req = request.get_json()
    existing_user = User.query.filter_by(email=req["email"]).first()
    # create gmail client
    gmail = Gmail(delegated_user="info@barscreen.tv")
    # generate password token
    password_token = generate_confirmation_token(existing_user.email)

    # Fill in email body and send email
    email_body = """Please click on the link to reset your BarScreen password. Link: {}""".format(
        url_for('dashboard.confirm_email', token=password_token),
    )
    gmail.send_email(to=existing_user.email,
                     subject="BarScreen Account", body=email_body)
    return jsonify({"success": True})


@dashboard.route("/account")
@login_required
def account():
    return render_template("dashboard/account.html")


@dashboard.route("/editprofile", methods=["POST"])
@login_required
def editprofile():
    req = request.get_json()
    user = User.query.filter_by(id=req["user_id"]).first()
    if request.method == "POST":
        if req["first_name"] != user.first_name:
            user.first_name = req["first_name"]
        if req["last_name"] != user.last_name:
            user.last_name = req["last_name"]
        if req["phone_number"] != user.phone_number:
            user.phone_number = req["phone_number"]
        db.session.commit()
    return jsonify({"success": True})


@dashboard.route("/editemail", methods=["POST"])
@login_required
def editemail():
    req = request.get_json()
    user = User.query.filter_by(id=req["user_id"]).first()
    if request.method == "POST":
        if req["email"] != user.email:
            user.email = req["email"]
        db.session.commit()
    return jsonify({"success": True})


@dashboard.route("/addpromo", methods=["POST", "GET"])
@login_required
def addpromo():
    """ Add Promo route. Adds clip to whatever the current show that is being edited. """
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
    return render_template("dashboard/addpromo.html", form=form, error=error, current_user=current_user)
