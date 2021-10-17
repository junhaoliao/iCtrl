# iCtrl

**SSH Remote Desktop Client / Web Service** (Previously known as **UG_Remote**)

## Disclaimer
Your SSH hosts and credentials will be stored locally on the computer you run the program with. 
Although we have been trying to protect your information with honest efforts, we are not cyber security experts and cannot guarantee the program is 100% bug-free. 

Please do not use the program on a public computer. 
We are not responsible for any irresponsible use of our program. 

## Authors
- Junhao Liao
- Kruzer Yizhong Xu
- Kevin Haoran Zhang
- Leo Jiaxing Li
- Richard Junjie Shen (Logo)



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
