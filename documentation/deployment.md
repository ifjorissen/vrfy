# How To Deploy
  * First, we're running this on a vm with Debian 8.1
  * Initially we'll use Nginx as a front-end server and gunicorn for Django/WSGI

# One-Time Setup

    sudo apt-get install build-essential nginx postgresql-9.4 python3 python3-pip python-virtualenv postgresql-server-dev-9.4
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
    
* modify `start.sh` in the project directory with the proper environment dir and project dir
