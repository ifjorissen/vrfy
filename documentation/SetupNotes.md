## Vrfy Local Dev Setup Notes
#### (mac osx)

### Quickstart
  * clone this project repo
  * (if you don't have python3 installed, `brew install python3`. if you don't have homebrew installed, do that...)
  * If you've already made a databse: start postgres database `pg_ctl start -D /usr/local/var/postgres`. Otherwise, skip down to the Start the Database / Create a Database & User section.
  * If you've already created a virtual environment, `cd <vrfy-dir>`, the project directory, and start the virtual environment. Otherwise, skip to the Python3 Virtual Env section and then head back here.
  * `pip install -r requirements.txt` this command installs the python libs for this project 
    * a note about this: the version of django-grappelli that were's using is not what's currently distributed with `pip install django-grapelli`. Running that will give you the latest stable release compatible with Django 1.7. Since we're using Django 1.8 and there's a stable grappelli branch available, we're grabbing v.2.7.x right from github with:  `pip install git+https://github.com/sehmaschine/django-grappelli.git@stable/2.7.x`
  * `npm install` this command installs the node modules required for this project (if you don't have node installed `brew install node`), check those out in package.json
  * `bower install` this command installs the bower components required for this project (if you don't have bower installed `npm install -g bower`), check those out in bower.json
  * `grunt` this command creates the files & folder necessary (e.g course/static/course)
  * `python3 manage.py collectstatic` this collects static files from the static folders and the bower_components directories (as per vrfy/settings.py).
  * Make initial db migrations: `python3 manage.py makemigrations`
  * Apply the migrations to the db: `python3 manage.py migrate`
  * If you want to access the admin interface, make a superuser: `python3 manage.py createsuperuser` (add `/admin` to see the admin interface) 
  * `python3 manage.py gruntserver`  this is a *custom* command that integrates the task runner grunt with the traditional runserver command provided by django (see [https://lincolnloop.com/blog/simplifying-your-django-frontend-tasks-grunt/] if you're curious). Grunt compiles all .scss files into .css, concatenates all .js files and puts them into the /static/ subdirectory of the course app. Whenever a change is made to a .js file in course/js (and respectively, a .scss file in course/sass) grunt recompiles everything and the changes are reflected in the browser (at localhost:8000).  Of course, you can always use `python3 manage.py runserver`, which runs the server using localhost at port 8000. 

### With Tango
  * install docker and boot2docker: `brew install docker boot2docker`. (get help with docker)[https://docs.docker.com/installation/mac/#from-your-command-line]  * get VirtualBox version ~ 4.6 (if you're developing on a mac)
  * clone Tango to your machine (the dist_docker branch, commit `eb18878d49c0ca718fc994919ed08b92aa00a77b`, see [how to clone old commit](http://stackoverflow.com/questions/1655361/how-to-clone-an-old-git-commit-and-some-more-questions-about-git))
  * Follow [their instructions](https://github.com/autolab/Tango/wiki/Tango-with-Docker) for getting Tango running with docker
  * In `vrfy/settings.py` change `TANGO_ADDRESS` to the Tango server's address, `TANGO_KEY` to one of the keys for the server and `TANGO_COURSELAB_DIR` to the directory where Tango will store its courselabs
  * When you start the server you may want to use sudo, ie: `sudo python restful-tango/server.py` to make sure it has permission to edit the courselabs. (If you're on a mac and using docker & boot2docker, you won't have to, though.)
  * change the setting 'VMMS_NAME' to 'VMMS_NAME = "localDocker"' in the Tango/config.py file (you should have created one, per the Tango instructions) 
  * `boot2docker up` (& follow instructions, if there are any)
  * `python restful-tango/server.py 3300`


##More help on Databases, Virtual Envs, etc.

### Python3 Virtual Env
Make a virtual environment for all the python packages we're using (if you're not sure what those are, read up on virtual environments). Check out the packages we're using for this project in requirements.txt
  * `mkdir ~/Envs/sds_vrfy`
  * `pyvenv ~/Envs/sds_vrfy`
  * and once you're in the directory where this project is, activate the virtual environment with: `source ~/Envs/sds_vrfy/bin/activate`

### Start the Database / Create a Database & User
  * install postgres if you don't already have it. (`brew install postgres`)
  * Start the postgres database server with: `pg_ctl start -D /usr/local/var/postgres` Note: `/usr/local/var/postgres` is the location of the database
  * View databases &  users with `psql -l` 
  * Create a database user with `createuser <username>`.
  * Create a database owned by a db user: `createdb -O <username> <dbname>`
  *  Note: the two commands above should correspond to the user and database in vrfy/settings.py under DATABASES. For this project's default settings, one would type: `createuser vrfy_dev_usr` and `createdb -O vrfy_dev_usr vrfy_dev`

### Set up Boot2Docker
  * `brew install boot2docker`
  * `boot2docker init`
  * `boot2docker start`
  * `eval "$(boot2docker shellinit)"`


### If you've already gotten everything installed and only need to get things up and running again and you need a little reminder:
  * In the Tango project: activate virtualenv, `boot2docker up`, `python restful-tango/server.py 3300`
  * In the vrfy project: perform necessary migrations & create a superuser, then `python3 manage.py gruntserver`

## Trouble (an incredibly incomprehenive list of things that sometimes go wrong & possible fixes)
  * if the command `python3 manage.py gruntserver` gives you some bs about a port and a database and connections, make sure postgres is running
  * if you're getting an error with Tango about virtual machines / permissions you're on a mac, make sure you've activated (& installed) boot2docker
  * if your database is freaking out, trying deleting everything in it (`python3 manage.py flush`) and then deleting all the migrations (migrations folders) and remaking the inital one


