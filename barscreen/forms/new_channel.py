from wtforms import StringField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired

from . import BSFileForm

class NewChannelForm(BSFileForm):
    """
    Form for creating a new Channel.
    """
    __fnattr__      = "channel_name"
    __fileattr__    = "channel_image"
    channel_name    = StringField("Channel Name", validators=[DataRequired()])
    category        = StringField("Category", validators=[DataRequired()])
    description     = TextAreaField("Description", validators=[DataRequired()], render_kw={"rows": 4})
    channel_image   = FileField("Channel Image", validators=[DataRequired()])
    submit          = SubmitField("Submit")
