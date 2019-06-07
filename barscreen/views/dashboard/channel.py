from flask import (request, render_template, jsonify)
from flask_login import login_required

from . import dashboard
from barscreen.database import db
from barscreen.database.channel import Channel


@dashboard.route("/channel")
@login_required
def channel():
    return render_template("dashboard/channel.html")


@dashboard.route("/create/get_channel", methods=["POST"])
@login_required
def get_channel():
    req = request.get_json()
    current_channel = Channel.query.filter_by(id=req["channel_id"]).first()
    return jsonify({'data': render_template('dashboard/channelmod.html', current_channel=current_channel)})
