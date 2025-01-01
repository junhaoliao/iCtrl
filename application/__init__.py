#  Copyright (c) 2021-2024 iCtrl Developers
# 
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.
import logging.config

import os
import sys

import datetime

from clp_logging.handlers import CLPFileHandler
from pathlib import Path
import yaml
from flask import Flask, Blueprint, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.serving import WSGIRequestHandler

timestamp = datetime.datetime.now()
file_name = timestamp.strftime("%Y-%m-%d-%H-%M")
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)
file_path = os.path.join(log_dir, f'ictrl_{file_name}.clp.zst')

try:
    with open('log_config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file.read())
    logging.config.dictConfig(config)
except Exception as ex:
    print("Logging setup failed with exception = ", ex)

logger = logging.getLogger(__name__)
#Setting the message to warning in case logging set up from dictConfig was not successful
logger.warning(f"Logging is set up with config={config}")

from .Profile.Profile import Profile

# enable persistent HTTP connections (keep-alive)
WSGIRequestHandler.protocol_version = "HTTP/1.1"

# launch the client from different path depending on whether the Python script has been packed into an executable
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'client'))
else:
    app = Flask(__name__, static_folder="../client/build")


@app.errorhandler(Exception)
def exception_handler(error):
    if isinstance(error, HTTPException):
        app.logger.exception(str(error))
        return error.get_response(), error.code

    app.logger.exception(error)
    return jsonify(error=str(error)), 500


@app.after_request
def handle_after_request(response: Flask.response_class):
    if response.content_type == 'application/json':
        app.logger.info(response.get_data(as_text=True))
    return response


app.secret_key = os.getenv('SECRET_KEY', os.urandom(16))

APP_PORT: int
LOCAL_AUTH_KEY: str
try:
    APP_PORT = int(sys.argv[1])
    LOCAL_AUTH_KEY = sys.argv[2]
except IndexError:
    logger.debug("Running in debug mode")
    APP_PORT = 5000
    LOCAL_AUTH_KEY = ''

os.environ['LOCAL_AUTH_KEY'] = LOCAL_AUTH_KEY

APP_HOST = '127.0.0.1'

profiles: Profile
if os.getenv('DBADDR') is not None:
    from .Profile.DBProfile import DBProfile

    profiles = DBProfile(app)
else:
    from .Profile.LocalProfile import LocalProfile

    profiles = LocalProfile()

api = Blueprint('api', __name__)

from .routes import *
