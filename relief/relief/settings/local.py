from .base import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
# Set the DJNGO_SETTINGS_MODULE env var to project.settings.local to run production settings
print("--------------- LOCAL DEVELOPMENT ------------------")
DEBUG = True


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

ALLOWED_HOSTS = ['*']

STATIC_ROOT = BASE_DIR / "staticfiles"

INSTALLED_APPS += [
    'debug_toolbar',
]

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# Set DB_USER and DB_PASSWORD env var to load user and password
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/usr/src/app/relief.sqlite'
    }
}


MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

FRESHBOOKS_CLIENT_ID = os.environ['FRESHBOOKS_CLIENT_ID']
FRESHBOOKS_CLIENT_SECRET = os.environ['FRESHBOOKS_CLIENT_SECRET']
FRESHBOOKS_REDIRECT_URI = os.environ['REDIRECT_URI']
print("LOCAL STATIC ROOT::", STATIC_ROOT)
print("LOCAL FRESHBOOKS CLIENT ID:: ", FRESHBOOKS_CLIENT_ID)
print("LOCAL FRESHBOOKS CLIENT SECRET:: ", FRESHBOOKS_CLIENT_SECRET)
print("LOCAL FRESHBOOKS REDIRECT URL:: ", FRESHBOOKS_REDIRECT_URI)
#  configure rest framework to not use authentication for local tests
REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S",
    "DATETIME_INPUT_FORMATS": ["%d-%m-%Y %H:%M"],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ]
}
