from flask import(abort, jsonify, request)

from . import roku
from barscreen.database.base import db
from barscreen.database.clip import Clip
from barscreen.database.loop import Loop
from barscreen.database.promo import Promo
from barscreen.database.show import Show
from barscreen.database.user import User
from barscreen.models.roku import ShortformVideo


@roku.route("/get_loops", methods=["GET"])
def get_loops():
    """
    Retrieves loops in Roku friendly format (see roku spec).
    """
    # Pull api key from request, and attempt to match it to a user.
    api_key = request.args.get("api_key")
    current_user = db.session.query(User).filter(
        User.api_key == api_key).first()
    if not all([api_key, current_user]):
        abort(404)
    # Return loops in API format.
    loops = [
        {"name": loop.name, "image_url": loop.image_url, "id": loop.id}
        for loop in db.session.query(Loop).filter(Loop.user_id == current_user.id).all()
    ]
    return jsonify({"status": "success", "loops": loops})


@roku.route("/pubs/loops/<loop_id>")
def get_loop(loop_id):
    """ Takes the pub id/loop id and returns a json payload that matches the feed spec """
    # Pull api key from request and attempt to match it to a user.
    api_key = request.args.get("api_key")
    current_user = db.session.query(User).filter(
        User.api_key == api_key).first()
    if not all([api_key, current_user]):
        abort(404)

    # Grab publisher id from user.
    publisher_id = current_user.id

    # Attempt to fetch request loop.
    loop = db.session.query(Loop).filter(
        Loop.id == loop_id, Loop.user_id == publisher_id).first()
    if not loop:
        abort(404)

    # Pull the last played clip dict from current loop.
    last_played = loop.get_last_played_clips()

    # Create json feed object in accordance with Roku specifications.
    json_feed = {
        "providerName": "BarscreenTV",
        "lastUpdated": str,
        "language": "en",
        "movies": [],
        "series": [],
        "shortFormVideos": [],
        "tvSpecials": [],
        "playlists": []
    }
    json_feed["lastUpdated"] = loop.last_updated

    # Iterate playlist and add clips or promos as needed.
    for item in loop.get_playlist_as_objects():
        
        # Pull the last played clip dict from current loop.
        last_played = loop.get_last_played_clips()
        

        # If item is a promo, add it with no further actions.
        if isinstance(item, Promo):
            # Turn item into shortform video.
            sf_video = ShortformVideo(item)

        # Shows require special handling for their clip order.
        else:
            # Grab the next clip for show and turn into shortform video.
            next_clip, last_played_clips = item.get_next_clip(last_played)
            sf_video = ShortformVideo(next_clip)

            # Update last played clips.
            loop.set_last_played_clips(last_played_clips)
            db.session.commit()
            
        # Add the formatted shortform video to the existing list.
        json_feed["shortFormVideos"].append(sf_video.formatted())


    # Add playlist object for all shortform videos.
    playlist = {
        "name": loop.name,
        "itemIds": [i["id"] for i in json_feed["shortFormVideos"]]
    }
    json_feed["playlists"].append(playlist)

    # Return json_feed as json
    return jsonify(json_feed)
