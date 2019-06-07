from . import db, BaseModel
from sqlalchemy.orm import validates


class Channel(BaseModel):
    """
    Channel Model
    """
    __tablename__ = "channel"

    name        = db.Column(db.String, nullable=False, unique=True)
    category    = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    image_url   = db.Column(db.String, nullable=True)
    shows       = db.relationship("show", backref="channel", lazy=True)

    @validates('image_data')
    def validate_image_data(self, key, image_data):
        if not image_data:
            raise AssertionError("No image data provided")
        # img_type = imghdr.what('', image_data)
        # if img_type != 'jpeg' and img_type != 'png':
        #     raise AssertionError(
        #         "Please use  a jpeg or a png file for a channel image")
        return image_data
