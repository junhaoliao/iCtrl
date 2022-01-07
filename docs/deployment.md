# Deployment of iCtrl on a Ubuntu Server (22.04) with Apache2

### Clone the Repository into the /var/www directory
```Shell
# with appropriate permissions (e.g. logged-in as root / www-data)
# if logging-in as www-data gives the following message:
# "This account is currently not available."
# We can change the default shell of www-data to make it available:
#   sudo chsh www-data
# enter a shell path such as "/bin/bash"

cd /var/www
git clone https://github.com/junhaoliao/iCtrl.git ictrl
```

### Add a user named "ictrl" to respect the permission of the other users on the same server
```Shell
sudo useradd ictrl
sudo usermod -a -G www-data ictrl
```

### Install Dependencies and build web page
```bash
cd /var/www/ictrl

# run as user ictrl
sudo su ictrl

# create a Python3 virtual environment
python3 -m pip install --user virtualenv
python3 -m virtualenv venv

# activate the virual environment
source venv/bin/activate

# install all backend depedencies
pip install -r requirements.txt

# install frontend dependencies
cd client
npm i
npm run build
```

### Install and Enable the Apache 2 module 'mod_wsgi'

```Shell
sudo apt update
sudo apt install libapache2-mod-wsgi-py3 -y

# enable the wsgi module
sudo a2enmod wsgi
# alternatively, use this on some other distributions
# sudo a2enmod mod-wsgi
```

### Apache2 Configuration Example

To add a config:

```Shell
sudo nano /etc/apache2/sites-available/ictrl.conf
```

ictrl.conf Content:

```ApacheConf
<VirtualHost *:80>
    ServerName ictrl.ca

    DocumentRoot /var/www/ictrl/client/build

    WSGIDaemonProcess ictrl_srv user=ictrl threads=20
    WSGIScriptAlias /api /var/www/ictrl/ictrl_srv.wsgi

    <Directory /var/www/ictrl>
        WSGIProcessGroup ictrl_srv
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    LogLevel warn
    ErrorLog ${APACHE_LOG_DIR}/ictrl_error.log
    CustomLog ${APACHE_LOG_DIR}/ictrl_custom.log combined
</VirtualHost>
```

### To Enable the Site Config

```Shell
sudo a2ensite ictrl
```

### Configure HTTPS / WSS
1. Generate An SSL Cert 
   Providers such as [Let's Encrypt](https://letsencrypt.org/) can be used. 
2. Copy the certs to the site directory to avoid permission issues
```Shell
sudo cp /etc/letsencrypt/live/junhao.ca/fullchain.pem .
sudo cp /etc/letsencrypt/live/junhao.ca/privkey.pem .

sudo chown www-data:www-data fullchain.pem privkey.pem
```

### Initialization of the Database
