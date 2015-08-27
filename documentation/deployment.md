# How To Deploy
  * First, we're running this on a vm with Debian 8.1
  * Initially we'll use Nginx as a front-end server and gunicorn for Django/WSGI

# One-Time Setup

    sudo apt-get install build-essential postgresql-9.4 python3 python3-pip python-virtualenv postgresql-server-dev-9.4 apache2 apache2-dev
    sudo adduser vrfy
    sudo -u vrfy -i
    virtualenv --python=/usr/bin/python3 py_env
    source py_env/bin/activate
    git clone https://github.com/ifjorissen/vrfy.git
    cd vrfy
    pip install -r requirements.txt
    cp config/settings_local.py.prod-example vrfy/settings_local.py
    ^D # end login session as vrfy
    # edit DB password
    sudo --user=postgres psql template1
    # create DB + user to match settings_local.py in production
    cd
    # download, build, and install Cosign signle-sign-on module
curl -O "http://tcpdiag.dl.sourceforge.net/project/cosign/cosign/cosign-3.2.0/cosign-3.2.0.tar.gz"
    tar -zxvf cosign-3.2.0.tar.gz
    cd cosign-3.2.0
    ./configure --enable-apache2=/usr/bin/apxs2
    # quick-n-dirty patch for apache 2.4
    sed s/remote_ip/client_ip/g -i filters/apache2/mod_cosign.c
    make
    sudo make install
    sudo mkdir /etc/apache2/include
    sudo cp vrfy/config/apache/cosign.conf /etc/apache2/include/
    sudo cp vrfy/config/apache/vhost.conf /etc/apache2/sites-available/vrfy.conf
    # installed certs from TIS; can't be stored in repo so not reproduced here
    sudo a2enmod proxy cosign ssl
    sudo a2ensite vrfy
    sudo service apache2 restart

  * modify `start.sh` in the project directory with the proper environment dir and project dir
  * Add a folder called `migrations` with a file called `__init__.py` to `course`, `catalog` and `ldap_auth`

#Tango
  * Generally follow the docs in our Readme.md
  * On our server, we had to use a weird command called `ksudo` instead of `sudo` which doesn't maintain maintaing your current working directory, so I had to change the addresses in `autodriver/Makefile` to be absolute(and change all of the `sudo`s to `ksudo`s
  * Since ksudo also doesn't respect virtual envs, you'll have to install your packages with `ksudo pip install -r /PATH/TO/Tango/requirements.txt -t /PATH/TO/YOUR/VIRTUALENV/lib/python2.7/site-packages`
    * The way the Tango instructions say to do it, the virtualenv folder is the same as the root Tango folder
  * install supervisor with `ksudo apt-get install supervisor`
  * make a file in `/etc/supervisor/conf.d/` called `tango.conf`
  
