from . import db, BaseModel

class Clip(BaseModel):
    """
    Clip Model
    """
    __tablename__ = "clip"
    
    name        = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    duration    = db.Column(db.Integer, nullable=False, default=0)
    clip_url    = db.Column(db.String, nullable=True)
    show_id     = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    image_url   = db.Column(db.String, nullable=True)
