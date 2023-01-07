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

# activate the virtual environment
activate_this = '/var/www/ictrl/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# insert the project path so that module 'application' can be found
sys.path.insert(0, '/var/www/ictrl/')

# read the config file
#  as we don't want to hard-code those sensitive data and commit them into Git
with open('/home/ictrl/ictrl.conf', 'r') as config_file:
    for line in config_file:
        if line.startswith('#'):
            continue

        try:
            name, value = line.strip().split('=')
            os.environ[name] = value
        except ValueError:
            pass

# now import the application
from application import app as application, api

application.register_blueprint(api)

# FIX_ME: testing code: comment out before publishing
# application.register_blueprint(api, url_prefix='/api')
# application.run(host='0.0.0.0', port=5000)
