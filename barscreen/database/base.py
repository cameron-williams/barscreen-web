from flask import current_app
from flask_sqlalchemy import SQLAlchemy

# Create sqlalchemy object as db.
db = SQLAlchemy()


class BaseModel(db.Model):
    """
    BaseModel for all barscreen models.
    """
    __abstract__ = True
    
    id              = db.Column(db.Integer, primary_key=True)
    date_created    = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_updated    = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    