##Python3 Virtual Env
	* `mkdir ~/Envs/sds_vrfy`
  * `pyvenv ~/Envs/sds_vrfy`
  * and once you're in the directory where this project is, activate the virtual environment with: `source ~/Envs/sds_vrfy/bin/activate`

##Start the Database / Create a Table
* `pg_ctl start -D /usr/local/var/postgres`
* `psql -l`  //lists databases
* `createuser <username>`
* `createdb -O <username> <dbname>`

**Use these names in the settings file**

####Running locally:
  * start postgres database should be something like `pg_ctl start -D /usr/local/var/postgres`, where `/usr/local/var/postgres` is the location of the database. 
  * In another tab/window `cd <vrfy-dir>` and start the virtual environment
  * `python manage.py collectstatic` this collects static files from the static folders and the webapps_assets and bower_components directories (as per webapps/settings.py).
  * if you're running this for the first time or have changed the models at all, make migrations (see below)
  * `python manage.py runserver` runs the server using localhost at port 8000. Add `/admin` to see the admin interface (which is all there really is to see right now, since the authentication is hardcoded in for this development environment) if you add some problems & problem sets and go back to the home page you'll be able to see the problem sets and problems on the main page

##### If there are migrations to make:
  * `python3 manage.py makemigrations <app_name>`
  * `python3 manage.py migrate`
  * `python3 manage.py syncdb`


Create a user for the admin interface:
`python3 manage.py createsuperuser`


Goals:
## To get tango to work:
If you don't have a linux machine: (get help)[https://docs.docker.com/installation/mac/#from-your-command-line]
`brew install boot2docker`
`boot2docker init`
`boot2docker start`
`eval "$(boot2docker shellinit)"`

Docker examples
Starts an niginx webserver, keeps the process running, publishes the ports, uses the files at the given path, and calls it mysite
`docker run -d -P -v $HOME/site:/usr/share/nginx/html --name mysite nginx`
`docker ps` //lists processes
`boot2docker ip` //boot2docker's ip

`docker pull ubuntu` //grab a linux distro

strip down sin as much as possible, leaving relevant stuff for examples(?)

make sure there's markdown support for the problem statements


make tornado webserver or 
add tango and / or some kind of python component to manage docker components (with an api that the django app connects to and submits / queries jobs)
