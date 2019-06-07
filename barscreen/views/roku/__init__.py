from flask import Blueprint

roku = Blueprint("roku", __name__, static_folder="../../static")



# Import all roku routes.
from . import base