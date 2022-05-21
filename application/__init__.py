#  Copyright (c) 2021-2022 iCtrl Developers
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

import os
import sys

from flask import Flask, Blueprint
from werkzeug.serving import WSGIRequestHandler

from .Profile import *

# enable persistent HTTP connections (keep-alive)
WSGIRequestHandler.protocol_version = "HTTP/1.1"

# launch the client from different path depending on whether the Python script has been packed into an executable
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'client'))
else:
    app = Flask(__name__, static_folder="../client/build")

app.secret_key = os.getenv('SECRET_KEY', os.urandom(16))

APP_PORT: int
LOCAL_AUTH_KEY: str
try:
    APP_PORT = int(sys.argv[1])
    LOCAL_AUTH_KEY = sys.argv[2]
except IndexError:
    APP_PORT = 5000
    LOCAL_AUTH_KEY = ''

APP_HOST = '127.0.0.1'

profiles: Profile
if os.getenv('DBADDR') is not None:
    profiles = DBProfile(app)
else:
    profiles = LocalProfile()

api = Blueprint('api', __name__)

from .routes import *
