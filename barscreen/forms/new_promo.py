from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired

from . import BSFileForm

class NewPromoForm(BSFileForm):
    """
    Basic form for submitting a new promotion.
    """
    __fnattr__   = "promo_name"
    __fileattr__ = "promo_file"
    promo_name   = StringField("Promo Name", validators=[DataRequired()])
    description  = StringField("Description", validators=[DataRequired()], render_kw={"rows": 4})
    promo_file   = FileField("Channel File", validators=[DataRequired()])
    submit       = SubmitField()