from flask import Flask, render_template, send_from_directory
from werkzeug.serving import WSGIRequestHandler

from application.Profile import Profile

# enable persistent HTTP connections (keep-alive)
WSGIRequestHandler.protocol_version = "HTTP/1.1"

app = Flask(__name__, static_folder="../client/build/static", template_folder="../client/build")
profiles = Profile()

from application.routes import *

if not app.debug:
    @app.errorhandler(404)
    def not_found(_):
        if request.path == '/icon.png':
            return send_from_directory(app.template_folder, 'icon.png')
        elif request.path == '/manifest.json':
            return send_from_directory(app.template_folder, 'manifest.json')
        else:
            print(request.path)
        return render_template('index.html')


    @app.route("/")
    def react():
        return render_template('index.html')
