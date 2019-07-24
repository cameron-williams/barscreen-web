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
    shows       = db.relationship("Show", backref="channel", lazy=True)
