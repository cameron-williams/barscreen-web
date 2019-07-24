"""
Base view.
This holds the not signed in pages for https://barscreen.tv/
"""
from flask import (request, Blueprint, render_template, current_app, flash)

from barscreen.database import db
from barscreen.database.user import User
from barscreen.forms.contact import ContactForm
from barscreen.forms.signup import SignupForm
from barscreen.services.google_clients import Gmail

base = Blueprint("base", __name__, static_folder="../static")

@base.route("/")
def index():
    return render_template("base/index.html")

@base.route("/about")
def about():
    return render_template("base/about.html")

@base.route("/features")
def features():
    return render_template("base/features.html")


@base.route("/contact", methods=["POST", "GET"])
def contact():
    form = ContactForm()
    if request.method == "POST" and form.validate_on_submit():
        g = Gmail(delegated_user="cam@barscreen.tv")
        msg = """
            New Contact Form Submission:
            Name: {}
            Email: {}
            Message: {}""".format(
            form.name.data,
            form.email.data,
            form.message.data,
        )
        g.send_email(to="info@barscreen.tv",
                     subject="New Contact Submission", body=msg)

    return render_template("base/contact.html", form=form)


@base.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignupForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_number=form.phone.data,
                email=form.email.data,
                company=form.company.data,
            )
            db.session.add(user)
            db.session.commit()
            g = Gmail(delegated_user="cam@barscreen.tv")
            msg = """
                New Sign Up:
                First Name: {}
                Last Name: {}
                Email: {}
                Phone Number: {}
                Company: {}""".format(
                form.first_name.data,
                form.last_name.data,
                form.email.data,
                form.phone.data,
                form.company.data,
            )
            g.send_email(to="info@barscreen.tv",
                         subject="New Sign Up", body=msg)
        except Exception:
            flash("Unknown error has occurred. Please try again.", category="error")
        flash("Your account is pending, if you are approved we will be in touch with your credentials. Please check email your email.", category="success")
    return render_template("base/signup.html", form=form)
