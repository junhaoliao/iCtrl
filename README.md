# iCtrl

**SSH Remote Desktop Client / Web Service** (Previously known as **UG_Remote**)

## Config the Flask Application with Apache2

### Install and Enable the Apache 2 module 'mod_wsgi'

```
sudo apt update
sudo apt install libapache2-mod-wsgi-py3 -y
sudo a2enmod mod-wsgi
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
