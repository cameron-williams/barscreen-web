import json
import re

from . import db, BaseModel
from .promo import Promo
from .show import Show


class Loop(BaseModel):
    __tablename__ = "loop"

    name = db.Column(db.String, nullable=False)
    playlist = db.Column(db.ARRAY(db.String), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lp_clips = db.Column(db.String, nullable=True)  # {show_id:clip_id, sid:cid}
    image_url = db.Column(db.String, nullable=True)

    def get_last_played_clips(self):
        if not self.lp_clips:
            return {}
        return json.loads(self.lp_clips)
        # clips = self.lp_clips.split("&")
        # out = {}
        # for x in clips:
        #     x = x.split("=")
        #     out[int(x[0])] = int(x[1])
        # return out

    def set_last_played_clips(self, d):
        """
        Since last_played_clips are stored as a string, this function will take
        a dict and stringify it before setting the new attribute value.
        """
        self.lp_clips = json.dumps(d)
        # self.lp_clips = "&".join(["=".join([str(k), str(d[k])]) for k in d])

    def get_playlist_as_objects(self):
        """
        Playlist is stored as an array of strings ([Promo_1, Show_2]).
        This function will return it as an array of the actual objects
        the string array represents.
        """
        playlist = []
        # Iterate items in playlist.
        for item in self.playlist:

            # Use regex to get id of item.
            media_id = re.search(r'\d+', item).group()

            # Match item id vs Shows or Promos depending what string is in it.
            if 'promo' in item.lower():
                obj = db.session.query(Promo).filter(
                    Promo.id == media_id
                ).first()
            else:
                obj = db.session.query(Show).filter(
                    Show.id == media_id
                ).first()
            # If we matched an object successfully add it to the output playlist.
            if obj:
                playlist.append(obj)

        # Return the newly created playlist of objects.
        return playlist
