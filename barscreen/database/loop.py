from . import db, BaseModel

class Loop(BaseModel):
    __tablename__ = "loop"

    name              = db.Column(db.String, nullable=False)
    playlist          = db.Column(db.ARRAY(db.String), nullable=False)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lp_clips          = db.Column(db.String, nullable=True) # sid=cid&sid=cid
    image_url         = db.Column(db.String, nullable=True)

    def get_last_played_clips(self):
        if not self.lp_clips:
            return {}
        clips = self.lp_clips.split("&")
        out = {}
        for x in clips:
            x = x.split("=")
            out[int(x[0])] = int(x[1])
        return out

    def set_last_played_clips(self, d):
        self.lp_clips = "&".join(["=".join([str(k), str(d[k])]) for k in d])
