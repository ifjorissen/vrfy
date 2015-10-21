"""
Django settings for vrfy project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '#yu7$c#_y#2sip5i@hi^#iocpoa0))m14@e3ob_#0&#rvj_)w+'
DEBUG = True
LOCAL_DEV = True
ALLOWED_HOSTS = ["localhost", "cs.reed.edu"]
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Admins & Email for the server
ADMINS = (('Alex', 'grantal@reed.edu'), ('Isabella', 'isjoriss@reed.edu'))
EMAIL_HOST = 'localhost'
SERVER_EMAIL = 'noreply@cs.reed.edu'
# SESSION_COOKIE_DOMAIN = '.localhost'
# Grappelli settings
GRAPPELLI_ADMIN_TITLE = "CS@Reed Admin"
GRAPPELLI_INDEX_DASHBOARD = "vrfy.dashboard.CustomIndexDashboard"
# MARKDOWN_EDITOR_SKIN = 'simple'

# Application definition

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'grappelli.dashboard',
    'grappelli',
    'django_markdown',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dbbackup',
    'vrfy',
    'vrfy.apps.LDAPAuthConfig',
    'vrfy.apps.CourseConfig',
    'vrfy.apps.CatalogConfig',
)

AUTHENTICATION_BACKENDS = (
    'ldap_auth.auth_backend.LDAPRemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'ldap_auth.auth_middleware.LDAPRemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'vrfy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.core.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vrfy.wsgi.application'


# Database Info
if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'vrfy_test',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '5432',
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'vrfy_dev',
            'USER': 'vrfy_dev_usr',
            'PASSWORD': 'pass',
            'HOST': 'localhost',
            'PORT': '5432',
        },
    }

# from django.utils import timezone
# Database backup Info
# def media_backup_filename(databasename, servername, timestamp, extension, wildcard):
#     print("media backup")
#     return "{}_media{}-{}{}".format(servername, databasename, timestamp, extension)
#     # pass

# def backup_filename(databasename, servername, timestamp, extension, wildcard):
#     print("backup filename")
#     return "{}_db-{}-{}{}".format(servername, databasename, timestamp, extension)
# pass

# DBBACKUP_FILENAME_TEMPLATE = backup_filename
# DB_NAME = "vrfy_dev"
# def backup_filename(databasename):
#     print("{}hi".format(databasename))
#     # return "{}-hi{}-{}{}".format(servername, databasename, timestamp, extension)
#     pass

DBBACKUP_SERVER_NAME = "cshw"
DBBACKUP_BACKUP_DIRECTORY = "/Users/ifjorissen/vrfy_proj/vrfy_backups/"

SERVER_EMAIL = 'isjoriss@reed.edu'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = 'staticfiles/'
STATIC_URL = '/static/'
MEDIA_ROOT = 'problem_assets/'
MEDIA_URL = '/problem_assets/'
STATICFILES_DIRS = (
    # os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "bower_components"),
)

# TANGO Settings (for more info see documentation/tango.md)

# address of the tango server
TANGO_ADDRESS = "http://localhost:3300/"
# key to access tango server
TANGO_KEY = "test"
# location of the tango courselabs folder
TANGO_COURSELAB_DIR = "/Users/ifjorissen/vrfy_proj/cmu_tango/courselabs/"
# name of the makefile to be called in Tango
MAKEFILE_NAME = "autograde-Makefile"
TANGO_DEFAULT_TIMEOUT = 30


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logging/django.log',
            'formatter': 'verbose'
        },
        'vrfy_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logging/vrfy.log',
            'formatter': 'verbose'
        },
        'ldap_auth_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logging/ldap_auth.log',
            'formatter': 'verbose'
        },
        'catalog_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logging/catalog.log',
            'formatter': 'verbose'
        },
        'course_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logging/course.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'propagate': True,
            'level': 'INFO',
        },
        'vrfy': {
            'handlers': ['vrfy_log', 'mail_admins'],
            'level': 'INFO',
        },
        'catalog': {
            'handlers': ['catalog_log', 'mail_admins'],
            'level': 'INFO',
        },
        'course': {
            'handlers': ['course_log', 'mail_admins'],
            'level': 'INFO',
        },
        'ldap_auth': {
            'handlers': ['ldap_auth_log', 'mail_admins'],
            'level': 'INFO',
        },
    }
}

# local overrides for production settings, etc.
try:
    from vrfy.settings_local import *
except ImportError as e:
    import sys
    print(
        "Could not import local settings: {}; using defaults".format(e),
        file=sys.stderr)
    pass
