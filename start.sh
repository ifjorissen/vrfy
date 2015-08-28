#!/bin/sh

#used for starting gunicorn on the server

BASE_DIR=`dirname $0`
VENV_DIR=$HOME/py_env

source $VENV_DIR/bin/activate

$VENV_DIR/bin/gunicorn --reload --bind localhost vrfy.wsgi:application
