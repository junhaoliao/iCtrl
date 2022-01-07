import os
import sys

from flask import Flask, Blueprint
from werkzeug.serving import WSGIRequestHandler

# enable persistent HTTP connections (keep-alive)
WSGIRequestHandler.protocol_version = "HTTP/1.1"

# launch the client from different path depending on whether the Python script has been packed into an executable
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'client'))
else:
    app = Flask(__name__, static_folder="../client/build")

app.secret_key = os.getenv('SECRET_KEY', os.urandom(16))

try:
    APP_PORT = sys.argv[1]
    APP_HOST = '127.0.0.1'

    from .Profile.LocalProfile import LocalProfile

    profiles = LocalProfile()
except IndexError:
    # TODO: might change this to 80 in production mode
    #   but it doesn't seem to be necessary at the moment
    APP_PORT = 5000
    APP_HOST = '0.0.0.0'

    from .Profile.DBProfile import DBProfile

    profiles = DBProfile(app)

api = Blueprint('api', __name__)

from .routes import *
