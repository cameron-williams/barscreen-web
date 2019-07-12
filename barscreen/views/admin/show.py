from flask import (abort, render_template, flash, request)
from flask_login import login_required

from . import admin
from barscreen.auth import requires_admin
from barscreen.database import db
from barscreen.database.channel import Channel
from barscreen.database.show import Show
from barscreen.forms.new_show import NewShowForm


@admin.route("/channels/<channel_id>/shows/<show_id>", methods=["GET", "POST"])
@login_required
@requires_admin
def show(channel_id, show_id):
    """
    Specific channel route, allows edits to specified channel.
    """
    current_show = db.session.query(Show).filter(
        Show.channel_id == channel_id,
        Show.id == show_id
    ).first()

    if not current_show:
        abort(404, {"error": "No show by that id. (id:{})".format(show_id)})
    return render_template("admin/show.html", current_show=current_show, channel_id=channel_id)


@admin.route("/channels/<channel_id>/shows/new", methods=["POST", "GET"])
@login_required
@requires_admin
def add_show(channel_id):
    """
    Add Show route.
    Adds show to whatever the current channel that is being edited.
    """
    form = NewShowForm()

    # On post create new Show.
    if request.method == "POST" and form.validate_on_submit():
        try:
            
            # Pull channel to associate this show with.
            channel = db.session.query(Channel).filter(
                Channel.id == channel_id
            ).first()
            
            # Add new show to channel show list.
            channel.shows.append(Show(
                name=form.show_name.data,
                description=form.description.data,
                lookback=int(form.lookback.data),
                order=form.order.data
            ))
            db.session.commit()

        except Exception as err:
            logging.error("Error creating show for channel {}: {} {}".format(channel.id, type(err), err))
            flash("Error creating show, please try again.", category="error")
            abort(400)

        flash("Show created successfully.", category="success")
    return render_template("admin/add_show.html", form=form)
