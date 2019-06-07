from flask import (abort, render_template, flash, request)
from flask_login import login_required

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.channel import Channel
from barscreen.database.show import Show
from barscreen.forms.newshow import NewShowForm



@admin.route("/channels/<channel_id>/<show_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def showid(channel_id, show_id):
    """ Specific channel route, allows edits to specified channel. """
    current_show = db.session.query(Show).filter(
        Show.channel_id == channel_id,
        Show.id == show_id
    ).first()

    if not current_show:
        abort(404, {"error": "No show by that id. (id:{})".format(show_id)})
    return render_template("admin/showid.html", current_show=current_show, channel_id=channel_id)

@admin.route("/channels/<channel_id>/addshow", methods=["POST", "GET"])
@login_required
@requires_admin
def addshow(channel_id):
    """ Add Show route. Adds show to whatever the current channel that is being edited. """
    error = None
    form = NewShowForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            current_channel = db.session.query(Channel).filter(
                Channel.id == channel_id
            ).first()
            current_channel.shows.append(Show(
                name=form.show_name.data,
                description=form.description.data,
                lookback=int(form.lookback.data),
                order=form.order.data
            ))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if 'duplicate key value violates unique constraint' in str(e):
                error = 'show name already registered.'
        flash("Show Created.", category="success")
    return render_template("admin/addshow.html", form=form, error=error)