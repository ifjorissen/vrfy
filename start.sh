#!/bin/sh

#used for starting gunicorn on the server

BASE_DIR=`dirname $0`
VENV_DIR=$BASE_DIR/../py_env

source $VENV_DIR/bin/activate

$VENV_DIR/bin/gunicorn --bind cshw.reed.edu:8000 vrfy.wsgi:application
