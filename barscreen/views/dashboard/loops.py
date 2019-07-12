from flask import (render_template, flash, request, json, abort)
from flask_login import (login_required, current_user)
import re
from werkzeug.utils import secure_filename

from . import dashboard
from barscreen.database import db
from barscreen.database.channel import Channel
from barscreen.database.loop import Loop
from barscreen.database.promo import Promo
from barscreen.database.show import Show
from barscreen.forms.new_promo import NewPromoForm
from barscreen.services.google_clients import GoogleStorage


@dashboard.route("/loops")
@login_required
def loops():
    return render_template("dashboard/loops.html")


@dashboard.route("/loops/<loop_id>")
@login_required
def editloop(loop_id):
    trends = Channel.query.order_by(Channel.id.desc()).limit(10).all()
    entertainments = Channel.query.order_by(Channel.id.desc()).filter(
        (Channel.category).like('Entertainment')).all()
    sports = Channel.query.order_by(Channel.id.desc()).filter(
        (Channel.category).like('Sports')).all()
    news = Channel.query.order_by(Channel.id.desc()).filter(
        (Channel.category).like('News')).all()
    loop_playlist = []
    current_loop = Loop.query.filter_by(id=loop_id).first()
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
        print(json.dumps(loop_playlist))
    return render_template("dashboard/editloop.html", loop_playlist=json.dumps(loop_playlist), current_loop=current_loop, current_user=current_user, trends=trends, entertainments=entertainments, sports=sports, news=news)


@dashboard.route("/loops/new", methods=["POST", "GET"])
@login_required
def addloop():
    
    trends = Channel.query.order_by(Channel.id.desc()).limit(10).all()
    entertainments = Channel.query.order_by(Channel.id.desc()).filter(
        (Channel.category).like('Entertainment')).all()
    sports = Channel.query.order_by(Channel.id.desc()).filter(
        (Channel.category).like('Sports')).all()
    news = Channel.query.order_by(Channel.id.desc()).filter(
        (Channel.category).like('News')).all()
    form = NewPromoForm()
    if request.method == "POST" and form.validate_on_submit():
        storage = GoogleStorage()
        try:
            fn = secure_filename(form.promo_file.data.filename)
            url = storage.upload_promo_video(
                name=fn, file=form.promo_file.data)

            # save vid and get still from it
            form.promo_file.data.save('/tmp/{}'.format(fn))
            still_img_path = ""
            # still_img_path = get_still_from_video_file(
            # "/tmp/{}".format(fn), 5, output="/var/tmp/{}".format(fn.replace(".mp4", ".png")))
            still_url = storage.upload_promo_image(
                name=still_img_path.split("/")[-1], image_data=open(still_img_path).read())

            current_user.promos.append(Promo(
                name=form.promo_name.data,
                description=form.description.data,
                clip_url=url,
                image_url=still_url,
            ))

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if 'duplicate key value violates unique constraint' in str(e):
                error = 'show name already registered.'
        flash("Promo Created.", category="success")
    return render_template("dashboard/add_loop.html", form=form, current_user=current_user, trends=trends, entertainments=entertainments, sports=sports, news=news)
