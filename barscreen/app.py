"""

Barscreen Web Application.

This is the web application that runs the Barscreen roku dashboard and admin menus.
https://barscreen.tv/


2019-06-06
"""

import logging
from flask import (Flask, render_template, request,
                   abort, jsonify, redirect, url_for)
# from models import db, Users
from flask_login import LoginManager, login_required, login_user, current_user
from flask_migrate import Migrate
from systemd.journal import JournaldLogHandler

from barscreen.auth import login_manager
from barscreen.config.env import (
    DATABASE_URI, DEBUG, SECRET_KEY, SUBDOMAIN_ROUTING)


# App factory.
def create_app():

    # Create Flask app.
    app = Flask("barscreen")

    # Initialize configuration from our config folder.
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': DATABASE_URI,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': SECRET_KEY,
        'DEBUG': DEBUG,
        'SUBDOMAIN_ROUTING': SUBDOMAIN_ROUTING
    })

    # Set up database config.
    from barscreen.database import db
    db.init_app(app)

    # Initialize login_manager.
    login_manager.init_app(app)
    login_manager.login_view = "dashboard.login"

    # Initialize flask_migrate.
    migrate = Migrate(app, db)


    # Import views.
    from barscreen.views import base
    from barscreen.views.admin import admin
    from barscreen.views.dashboard import dashboard
    from barscreen.views.roku import roku

    # Register blueprints. Add url prefixes or subdomain routing based on SUBDOMAIN_ROUTING flag.
    app.register_blueprint(base.base)
    app.register_blueprint(base.base)
    app.register_blueprint(admin, url_prefix="/ad" if not SUBDOMAIN_ROUTING else None,
                           subdomain="admin" if SUBDOMAIN_ROUTING else None)
    app.register_blueprint(dashboard, url_prefix="/dash" if not SUBDOMAIN_ROUTING else None,
                           subdomain="dashboard" if SUBDOMAIN_ROUTING else None)
    app.register_blueprint(roku, url_prefix="/roku" if not SUBDOMAIN_ROUTING else None,
                           subdomain="roku" if SUBDOMAIN_ROUTING else None)

    # Add journald logging support to default Flask logger.
    journald_handler = JournaldLogHandler()
    journald_handler.setFormatter(logging.Formatter(
        '[%(levelname)s::%(file)s::%(line)s] %(message)s'
    ))
    journald_handler.setLevel(logging.WARN)
    app.logger.addHandler(journald_handler)

    # Custom error page for ANY app 404.
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html")

    return app
