from flask import (abort, jsonify, render_template,
                   request, flash, redirect, url_for)
from flask_login import login_required, logout_user
from urllib import unquote_plus

from . import admin
from barscreen.auth import (
    requires_admin, generate_confirmation_token, confirm_token)
from barscreen.database import db
from barscreen.database.user import User
from barscreen.forms.password import CreatePassword
from barscreen.services.google_clients import Gmail


@admin.route("/")
@login_required
@requires_admin
def admin_index():
    users = db.session.query(User).all()
    return render_template("admin/admin.html", users=users)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dashboard.login'))


@admin.route("/approve_user", methods=["POST"])
@login_required
@requires_admin
def approve_user():
    # Try and pull user using email from request json payload.
    req = request.get_json()
    user = db.session.query(User).filter(
        User.email == req.get("email")).first()

    # Ensure we have a user object.
    if not user:
        abort(404, "no user with that email")

    # Check if user is confirmed already.
    if user.confirmed:
        abort(400, "user is already confirmed")

    # Send confirmation email.
    # create gmail client
    gmail = Gmail(delegated_user="info@barscreen.tv")
    # generate password token
    password_token = generate_confirmation_token(user.email)

    # Fill in email body and send email
    email_body = """Congratulations you have been approved for a Barscreen account! Below is a link to create a password. Your email will be used for your username. Link: {}""".format(
        url_for('dashboard.confirm_email', token=password_token),
    )
    gmail.send_email(to=user.email,
                     subject="BarScreen Account", body=email_body)
    return jsonify({"success": True})


@admin.route("/confirm/<token>", methods=["GET", "POST"])
@login_required
@requires_admin
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
    except:
        flash('The confirmation link is invalid or has expired.', category='danger')
        return redirect(url_for('base.signup'))

    # pull user associated with token
    user = db.session.query(User).filter(User.email == email).first()
    if not user:
        abort(400, 'Invalid token.')
    if user.confirmed:
        flash('Account already confirmed. Please log in.', category="success")
        return redirect(url_for('dashboard.login'))

    # if form submit, add new password to user and redirect them to dashboard
    if request.method == "POST" and form.validate_on_submit():
        user.set_password(form.password.data)
        user.confirmed = True
        db.session.commit()
        flash("Password set successfully.", category="success")
        return redirect(url_for('dashboard.index'))
    return render_template("dashboard/password.html", form=form, token=token)


@admin.route("/user/<user_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def user(user_id):
    current_user = db.session.query(User).filter(User.id == user_id).first()
    if not current_user:
        abort(404, {"error": "User not found"})
    if request.method == 'POST':
        data = {unquote_plus(k.split("=")[0]): unquote_plus(
            k.split("=")[1]) for k in request.get_data().split("&")}
        if data["name"] in ('confirmed', 'ads'):
            if data['value'].lower() == 'false':
                data['value'] = False
            else:
                data['value'] = True
        setattr(current_user, data["name"], data["value"])
        db.session.commit()
        return ''
    return render_template("admin/user.html", current_user=current_user)
