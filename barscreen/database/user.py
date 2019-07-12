from .base import db, BaseModel
from barscreen.auth import (hash_password, verify_password)

class User(BaseModel):
    """
    Barscreen User Model.
    """
    __tablename__ = "user"

    # Attributes.
    first_name      = db.Column(db.String, nullable=False)
    last_name       = db.Column(db.String, nullable=False)
    phone_number    = db.Column(db.String, nullable=False)
    email           = db.Column(db.String, nullable=False, unique=True)
    company         = db.Column(db.String, nullable=False)
    ads             = db.Column(db.BOOLEAN, default=False)
    confirmed       = db.Column(db.BOOLEAN, default=False)
    confirmed_on    = db.Column(db.DateTime, nullable=True)
    password        = db.Column(db.CHAR(128), nullable=True)
    api_key         = db.Column(db.String, nullable=True)

    # Relationships.
    promos  = db.relationship("Promo", backref="user", lazy=True)
    loops   = db.relationship("Loop", backref="user", lazy=True)

    # Administrator flag.
    admin = db.Column(db.BOOLEAN, default=False)

    def __init__(self, first_name, last_name, phone_number, email, company, confirmed_on=None, admin=None, password=None, ads=False, confirmed=False):
        self.first_name     = first_name
        self.last_name      = last_name
        self.phone_number   = phone_number
        self.company        = company
        self.email          = email
        self.ads            = ads
        self.confirmed      = confirmed
        self.password       = password

        if admin:
            self.admin = admin

        if confirmed_on:
            self.confirmed_on = confirmed_on

    def __repr__(self):
        return '<User {}>'.format(self.email)

    @property
    def is_authenticated(self):
        return self.confirmed

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password = hash_password(password)
        return True
    
    def check_password(self, password):
        return verify_password(self.password, password)
