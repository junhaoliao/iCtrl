import os
import sys

from flask import Flask, send_from_directory
from werkzeug.serving import WSGIRequestHandler

# enable persistent HTTP connections (keep-alive)
WSGIRequestHandler.protocol_version = "HTTP/1.1"

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'client'))
else:
    app = Flask(__name__, static_folder="../client/build")

app.secret_key = os.getenv('SECRET_KEY', os.urandom(16))

try:
    APP_PORT = sys.argv[1]
    APP_HOST = '127.0.0.1'

    from .LocalProfile import LocalProfile

    profiles = LocalProfile()
except IndexError:
    # TODO: change this to 80 in production mode
    APP_PORT = 5000
    APP_HOST = '0.0.0.0'

    # fixme: change this
    from .DBProfile import DBProfile
    profiles = DBProfile(app)

from .routes import *

if not app.debug:
    # Reference: https://stackoverflow.com/questions/44209978/serving-a-front-end-created-with-create-react-app-with
    # -flask
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
