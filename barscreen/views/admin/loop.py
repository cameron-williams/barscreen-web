from flask import (render_template, abort, json, request, flash, jsonify)
from flask_login import login_required
import re

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.loop import Loop
from barscreen.database.promo import Promo
from barscreen.database.show import Show
from barscreen.database.user import User
from barscreen.services.google_clients import GoogleStorage


@admin.route("/user/<user_id>/addloop")
@login_required
@requires_admin
def addloop(user_id):
    current_user = db.session.query(User).filter(
        User.id == user_id
    ).first()
    shows = Show.query.all()
    promos = Promo.query.filter_by(user_id=user_id).all()
    return render_template("admin/addloop.html", current_user=current_user, shows=shows, promos=promos)


@admin.route("/user/<user_id>/loop/<loop_id>")
@login_required
@requires_admin
def editloop(user_id, loop_id):
    current_loop = db.session.query(Loop).filter(
        Loop.id == loop_id
    ).first()
    current_user = db.session.query(User).filter(
        User.id == user_id
    ).first()
    shows = db.session.query(Show).all()
    promos = db.session.query(Promo).filter(
        Promo.user_id == user_id
    ).all()
    loop_playlist = []
    if not current_loop:
        abort(404, {"error": "No channel by that id. (id:{})".format(loop_id)})
    for i in current_loop.playlist:
        media_id = re.search(r'\d+', i).group()
        if 'promo' in i.lower():
            promo = db.session.query(Promo).filter(
                Promo.id == media_id).first()
            # if promo
            if not promo:
                continue
            loop_playlist.append(
                {'id': promo.id, 'name': promo.name, 'image_url': promo.image_url, 'type': 'promo'})
        else:
            show = Show.query.filter_by(id=media_id).first()
            loop_playlist.append({'id': show.id, 'name': show.name,
                                  'image_url': show.clips[-1].image_url, 'type': 'show'})
    return render_template("admin/editloop.html", loop_playlist=json.dumps(loop_playlist), current_loop=current_loop, current_user=current_user, shows=shows, promos=promos)


@admin.route("/submit_loop", methods=["POST", "PUT"])
@login_required
def submit_loop():
    req = request.get_json()
    current_user = db.session.query(User).filter(
        User.id == req.get("user_id")
    ).first()
    image_url = None
    if req["image_data"]:
        # write file locally
        with open("/tmp/uploaded_image.png", "wb") as f:
            f.write(req["image_data"].split(",")[-1].decode("base64"))
        # upload file to cdn
        storage = GoogleStorage()
        image_url = storage.upload_loop_image(
            req["name"] + ".png", open("/tmp/uploaded_image.png").read())
    if request.method == "POST":
        # write file locally
        print(image_url)
        try:
            current_user.loops.append(Loop(
                name=req["name"],
                playlist=req["playlist"],
                image_url=image_url
            ))
            db.session.commit()
        except Exception as err:
            print(err)
            abort(400, err)
    if request.method == "PUT":
        loop = Loop.query.filter_by(id=req["loop_id"]).first()
        if req["name"] != loop.name:
            loop.name = req["name"]
        if req["playlist"] != loop.playlist:
            loop.playlist = req["playlist"]
        if image_url and image_url != loop.image_url:
            loop.image_url = image_url
        db.session.commit()
    return jsonify({"success": True})
