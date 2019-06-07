from . import db, BaseModel


class Show(BaseModel):
    """
    Channel Show Model
    """
    __tablename__ = "show"

    name        = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    lookback    = db.Column(db.Integer, default=1)
    order       = db.Column(db.String, default="recent")
    channel_id  = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    clips       = db.relationship("clip", backref="show", lazy=True)

    def __repr__(self):
        return '<Show {}>'.format(self.name)

    def get_id(self):
        return str(self.id)
