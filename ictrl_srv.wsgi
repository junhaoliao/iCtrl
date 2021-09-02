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
with open('ictrl.conf', 'r') as config_file:
    for line in config_file:
        if line.startswith('#'):
            continue

        try:
            name, value = line.strip().split('=')
            os.environ[name] = value
        except ValueError:
            pass

# setup the SSL certificate and key path
os.environ['SSL_CERT_PATH'] = '/var/www/ictrl/fullchain.pem'
os.environ['SSL_KEY_PATH'] = '/var/www/ictrl/privkey.pem'

# now import the application
from application import app as application, api

application.register_blueprint(api)
