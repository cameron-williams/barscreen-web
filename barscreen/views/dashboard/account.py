"""
Account related routes.
"""
from flask import (abort, request, jsonify, render_template,
                   flash, redirect, url_for)
from flask_login import (login_required, current_user)

from . import dashboard
from barscreen.auth import (confirm_token, generate_token, InvalidTokenError)
from barscreen.database import db
from barscreen.database.user import User
from barscreen.forms.password import CreatePassword
from barscreen.services.google_clients import Gmail


@dashboard.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    Account Route.
    Displays account information.
    """
    return render_template("dashboard/account.html")


@dashboard.route("/account/edit", methods=["POST"])
def edit_account():
    """
    Account edit route.
    """
    print("fucking HELLO?")
    payload = request.get_json()
    user = db.session.query(User).filter(User.id==payload.get("user_id")).first()
    if not user:
        abort(404)

    # Iterate keys in POST payload.
    for attr_name, new_value in payload.iteritems():
        
        # If attr matches a User attribute continue to edit.
        if hasattr(user, attr_name):

            # If existing value doesn't equal the new one, change it.
            if getattr(user, attr_name) != new_value:
                setattr(user, attr_name, new_value)
    db.session.commit()
    return jsonify({"success": True})


@dashboard.route("/account/confirm/<token>", methods=["GET", "POST"])
@login_required
def confirm_account(token):
    # On the get request we will have the token from the route <token> but the form will not have it
    # so we need to set it there.
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
    user = db.session.query(User).filter(User.email == email).first()
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


@dashboard.route("/account/reset_password", methods=["POST"])
def reset_password():
    req = request.get_json()
    # If there isn't a user key in the request abort 404.
    if not req.get("user"):
        abort(404)
    # Try and match email to a user.
    user = db.session.query(User).filter(User.email == req.get("email")).first()
    if not user:
        flash("No account found by that email.")
        return jsonify({"success": False})

    # Create gmail client.
    gmail = Gmail(delegated_user="info@barscreen.tv")
    # Generate password token.
    password_token = generate_token(user.email)

    # Fill in email body and send email.
    email_body = """Please click on the link to reset your BarScreen password.\n\nLink: {}""".format(
        url_for('dashboard.confirm_account', token=password_token),
    )
    gmail.send_email(to=user.email,
                     subject="BarScreen Account", body=email_body)
    return jsonify({"success": True})


@dashboard.route("/account/change_password", methods=["GET", "POST"])
def asdf():
    pass
