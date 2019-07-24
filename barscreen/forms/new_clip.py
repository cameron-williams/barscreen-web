from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired

from . import BSFileForm

class NewClipForm(BSFileForm):
    """
    Basic form for submitting a new clip.
    """
    __fnattr__   = "clip_name"
    __fileattr__ = "clip_file"
    clip_name    = StringField("Clip Name", validators=[DataRequired()])
    description  = TextAreaField("Description", validators=[DataRequired()], render_kw={"rows": 4})
    clip_file    = FileField("Channel File", validators=[DataRequired()])
    submit       = SubmitField("Submit")
