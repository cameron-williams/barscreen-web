from flask import Blueprint

dashboard = Blueprint("dashboard", __name__, static_folder="../../static")

# Import all dashboard routes.
from . import (account, base, channel, loops)