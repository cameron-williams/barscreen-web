from. import db, BaseModel

class Promo(BaseModel):
    __tablename__ = "promo"
    
    name        = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    duration    = db.Column(db.String, nullable=True)
    clip_url    = db.Column(db.String, nullable=True)
    image_url   = db.Column(db.String, nullable=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)