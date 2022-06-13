# Deployment of iCtrl on a Ubuntu Server (22.04) with Apache2

### Install Dependencies
```Shell
sudo apt update
sudo apt install git apache2 python3-pip libapache2-mod-wsgi-py3 libssl-dev -y

# enable the wsgi module
sudo a2enmod wsgi
# alternatively, use this on some other distributions
# sudo a2enmod mod-wsgi
```

### Add a user named "ictrl" to respect the permission of the other users on the same server
```Shell
sudo useradd ictrl
sudo usermod -a -G www-data ictrl

# change the default shell of ictrl to "/bin/bash"
sudo chsh ictrl
```

### Clone the Repository into the /var/www directory
```Shell
sudo chown -R www-data:www-data /var/www
sudo chmod -R 775 /var/www

cd /var/www
git clone https://github.com/junhaoliao/iCtrl.git ictrl
```

### Install Dependencies and build web page
```Shell
# with appropriate permissions (e.g. logged-in as ictrl)

cd /var/www/ictrl

# create a Python3 virtual environment
python3 -m pip install --user virtualenv
python3 -m virtualenv venv

# activate the virual environment
source venv/bin/activate

# install all backend depedencies
pip install -r requirements.txt

# if Node.js is not installed, follow
# https://github.com/nodesource/distributions/blob/master/README.md#debinstall

# install frontend dependencies
cd client
npm i
npm run build

# build websockify for ssh tunnel
cd /var/www/ictrl
git submodule init
git submodule update
cd application/websockify-other/c
make
```

### Apache2 Configuration Example

Add a config:

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
cd /var/www/ictrl

sudo cp /etc/letsencrypt/live/junhao.ca/fullchain.pem .
sudo cp /etc/letsencrypt/live/junhao.ca/privkey.pem .

sudo chown www-data:www-data fullchain.pem privkey.pem
```

### Initialization of the Database
1. Install the PSQL DBMS
    ```Shell
    sudo apt update
    sudo apt install postgresql postgresql-contrib -y
    ```
2. Change the DB user password
    ```Shell
    # take a note of the password because we need to put it in a configuration 
    # (see Configure the iCtrl Backend Server)
    sudo passwd postgresql
    ```

3. Edit `/etc/postgresql/14/main/pg_hba.conf` to allow local connections

    Find the lines and make sure the authentication METHOD is set to trust.
    ```
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            trust
    ```

### Configure the iCtrl Backend Server
Edit `/var/www/ictrl/ictrl.conf`. An example configuration is shown below
```
# setup DB password and url
DBPASSWD=<THE_PASSWORD_YOU_SET_IN_"Initialization of the Database">
DBADDR=localhost:5432

# setup email credentials for verifications
SENDER_SERVER=<SENDER_SERVER>
SENDER_PORT=<SENDER_PORT>
SENDER_EMAIL=<EMAIL_ADDRESS>
SENDER_PASSWD=<EMAIL_PASSWORD>

# setup the SSL certificate and key path
SSL_CERT_PATH=/var/www/ictrl/fullchain.pem
SSL_KEY_PATH=/var/www/ictrl/privkey.pem
```
