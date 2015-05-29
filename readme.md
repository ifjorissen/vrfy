##Python3 Virtual Env
	`mkdir ~/Envs/sds_vrfy`
  `pyvenv ~/Envs/sds_vrfy`
  `source ~/Envs/sds_vrfy/bin/activate`

##Start the Database / Create a Table
`pg_ctl start -D /usr/local/var/postgres`
`psql -l`  //lists databases
`createuser <username>`
`createdb -O <username> <dbname>`

**Use these names in the settings file**

####Running locally:
  * start postgres database should be something like `pg_ctl start -D /usr/local/var/postgres`, where `/usr/local/var/postgres` is the location of the database. 
  * In another tab/window `cd <webapps-dir>` and start the virtual environment
  * `python manage.py collectstatic` this collects static files from the static folders and the webapps_assets and bower_components directories (as per webapps/settings.py).
  * `python manage.py runserver` runs the server using localhost at port 8000.  

##### If there are migrations to make:
  * `python3 manage.py makemigrations <app_name>`
  * `python3 manage.py migrate`
  * `python3 manage.py syncdb`


Create a user for the admin interface:
`python3 manage.py createsuperuser`



Goals:
strip down sin as much as possible, leaving relevant stuff for examples(?)

make sure there's markdown support for the problem statements


make tornado webserver or 
add tango and / or some kind of python component to manage docker components (with an api that the django app connects to and submits / queries jobs)
