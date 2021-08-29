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

try:
    _ = sys.argv[1]
    from .LocalProfile import LocalProfile

    profiles = LocalProfile()
except IndexError:
    # fixme: change this
    from .LocalProfile import LocalProfile

    profiles = LocalProfile()

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
