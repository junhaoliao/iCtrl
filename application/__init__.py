from flask import Flask, render_template

from application.Profile import Profile

app = Flask(__name__, static_folder="../client/build/static", template_folder="../client/build")
profiles = Profile()

from application.routes import *

if not app.debug:
    @app.route("/")
    def react():
        return render_template('index.html')
