from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length

from . import BSFileForm

class NewLoopForm(BSFileForm):
    """
    Form for creating a new Loop.
    """
    __fnattr__      = "loop_name"
    __fileattr__    = "loop_image"
    loop_name       = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Loop Name", "size": 30})
    loop_image      = FileField("Image", validators=[DataRequired()])
    loop_data       = StringField("Data", validators=[DataRequired()], render_kw={"hidden": True})
    submit          = SubmitField("Submit", render_kw={"class": "dash_button"})


class NewLoopFormDashboard(FlaskForm):
    """
    Form for creating a new Loop on the dashboard.
    Main difference is the string loop_image field, since the image for dashboard
    loops is a b64 string created from canvas.
    """
    __fnattr__      = "loop_name"
    __fileattr__    = "loop_image"
    loop_name       = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Title", "size": 20})
    loop_image      = StringField("Image", validators=[DataRequired()], render_kw={"hidden": True})
    loop_data       = TextAreaField("Data", validators=[DataRequired()], render_kw={"hidden": True})
    submit          = SubmitField("Save", render_kw={"class": "dash_button"})



class UpdateLoopForm(BSFileForm):
    """
    Form for updating an existing Loop.
    """
    __fnattr__      = "loop_name"
    __fileattr__    = "loop_image"
    loop_name       = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Loop Name", "size": 30})
    loop_image      = FileField("Image")
    loop_data       = StringField("Data", validators=[DataRequired()], render_kw={"hidden": True})
    submit          = SubmitField("Submit", render_kw={"class": "dash_button"})

class UpdateDashboardLoopForm(FlaskForm):
    """
    Form for updating dashboard loops.
    """
    __fnattr__      = "loop_name"
    __fileattr__    = "loop_image"
    loop_name       = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Title", "size": 20})
    loop_image      = StringField("Image", render_kw={"hidden": True})
    loop_data       = TextAreaField("Data", validators=[], render_kw={"hidden": True})
    submit          = SubmitField("Save", render_kw={"class": "dash_button"})