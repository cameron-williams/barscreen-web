from random import choice

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
    clips       = db.relationship("Clip", backref="show", lazy=True)

    def __repr__(self):
        return '<Show {}>'.format(self.name)

    def get_id(self):
        return str(self.id)
    
    def get_next_clip(self, last_played_clips):
        """
        Shows have somewhat complicated clip handling. Every time a show is "called" from a roku device
        it will return a clip that will be shown. Depending on the Show's lookback and order, this will
        vary greatly. This function will take both attributes and return the correct clip that should be
        played next (while also referencing the passed last_played_clips argument.)

        Returns next_clip (next clip to play), last_played_clips (updated last played clips)
        """
        # Holds next clip.
        next_clip = None

        # Get the last played clip for this show id.
        last_played_clip_id = last_played_clips.get(str(self.id))

        # Handle random clip selection (order=random).
        if self.order == "random":
            # Get all available clips (total number of clips limited by lookback) as a dictionary of {clip_id: Clipobject}
            available_clips = {}
            for clip in list(reversed(self.clips))[:self.lookback]:
                available_clips[clip.id] = clip

            # Check if there is a last played clip and if the last played clip for this show is in our avilable clips, if it is remove it.
            if last_played_clip_id and last_played_clip_id in available_clips:
                available_clips.pop(last_played_clip_id)

            # Choose the next clip at random from remaining choices.
            next_clip = choice(available_clips.values())

            
        # Handles recent clip selection (order=recent)
        else:
            # Get all available clips (total number of clips limited by lookback)
            available_clips = list(reversed(self.clips))[:self.lookback]

            # If we don't have a last_played_clip_id, set next_clip to first available clip.
            if not last_played_clip_id:
                next_clip = available_clips[0]

            # We have a last played clip id, so we have to figure out what's next to play.
            else:

                # Find the index the last played clip is at in our available clips selection
                clip_index = None
                for index, clip in enumerate(available_clips):
                    if clip.id == last_played_clip_id:
                        clip_index = index
                        break

                # If no index, set next clip to first available clip.
                if not clip_index:
                    next_clip = available_clips[0]
                
                ## We have a valid index, grab the next clip in the list (or the first one if we have reached the end of the list).
                # Handles clip index being at the end of available clips.
                if clip_index + 1 == len(available_clips):
                    next_clip = available_clips[0]

                # Clip isn't at the end, grab next index.
                else:
                    next_clip = available_clips[clip_index+1]
        
        # Update last played clips with this newly chosen clip.
        last_played_clips[str(self.id)] = next_clip.id
        
        return next_clip, last_played_clips