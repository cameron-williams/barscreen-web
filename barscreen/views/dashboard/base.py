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
