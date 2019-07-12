"""
Account related forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, EqualTo

class CreatePassword(FlaskForm):
    """
    Basic form for submitting a password.
    """
    token = HiddenField("Submit Token", validators=[DataRequired()])
    password = PasswordField("Password",
                             validators=[DataRequired(), EqualTo(fieldname='confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Submit")


class ProfileUpdateForm(FlaskForm):
    """
    Form for updating user profile attributes on the dashboard.
    """
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    save = SubmitField("Save", render_kw={"class": "dash_button"})
