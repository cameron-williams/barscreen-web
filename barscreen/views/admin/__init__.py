from flask import Blueprint

admin = Blueprint("admin", __name__, static_folder="../../static")



# Import all admin routes.
from . import (base, channel, clip, loop, promo, show)