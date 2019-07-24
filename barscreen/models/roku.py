"""

Roku Shortform Video Specefications.

Roku shortform video is a video that is usually less than 20 minutes long. This accounts
for most of the media on barscreen.

The following link has all the objects in this file.
https://developer.roku.com/en-ca/docs/specs/direct-publisher-feed-specs/json-dp-spec.md

"""
from barscreen.database.promo import Promo
from barscreen.database.clip import Clip

# class Video(object):
#     """
#     Single video file object.
#     """
#     url = str
#     quality = str
#     videoType = str


# class Content(object):
#     """
#     Represents the details of a single video object.
#     """
#     dateAdded = str
#     videos = list()
#     duration = int
#     captions = list()

class ShortformVideo(object):
    # Required attributes.
    id                  = str
    title               = str
    content             = str
    thumbnail           = str
    shortDescription    = str
    releaseDate         = str
    longDescription     = str

    # Optional attributes.
    tags    = str
    genres  = str
    creduts = str

    def __init__(self, obj):
        # Verify passed arg is a Promo or Show.
        if not any([isinstance(obj, Promo), isinstance(obj, Clip)]):
            raise AssertionError("invalid arg type for Shortform Video: {}, must be Show or Promo".format(type(obj)))
        
        # Set self attributes from given obj.
        self.id                 = obj.id
        self.title              = obj.name
        self.content            = obj.clip_url
        self.thumbnail          = obj.image_url
        self.shortDescription   = obj.description
    
    def formatted(self):
        """
        Using self attributes returns a formatted shortform video.
        """
        # Holds formatted shortform video.
        formatted_output = dict()
        # Iterate each attribute in self and add to output before returning.
        for k, v in self.__dict__.iteritems():
            formatted_output[k] = v
        return formatted_output    
