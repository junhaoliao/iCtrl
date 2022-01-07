# Deployment of iCtrl on a Ubuntu Server (22.04) with Apache2

### Clone the Repository into the /var/www directory
```
# with appropriate permissions (e.g. logged-in as root / www-data)
# if logging-in as www-data gives the following message:
# "This account is currently not available."
# We can change the default shell of www-data to make it available:
#   sudo chsh www-data
# enter a shell path such as "/bin/bash"

cd /var/www
git clone https://github.com/junhaoliao/iCtrl.git ictrl_srv
```

### Add a user named "ictrl_srv" to respect the permission of the other users on the same server
```
sudo useradd ictrl_srv
sudo usermod -a -G www-data ictrl_srv
```

### Install and Enable the Apache 2 module 'mod_wsgi'

```
sudo apt update
sudo apt install libapache2-mod-wsgi-py3 -y

# enable the wsgi module
 sudo a2enmod wsgi
# alternatively, use this on some other distributions
# sudo a2enmod mod-wsgi
```

### Apache2 Configuration Example

To add a config:

```
sudo nano /etc/apache2/sites-available/ictrl.conf
```

ictrl.conf Content:

```
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

```
sudo a2ensite ictrl
```
