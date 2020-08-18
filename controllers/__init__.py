from flask import Blueprint

routes = Blueprint('routes', __name__)

from .statistics_controller import *