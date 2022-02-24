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
with open('/var/www/ictrl/ictrl.conf', 'r') as config_file:
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
