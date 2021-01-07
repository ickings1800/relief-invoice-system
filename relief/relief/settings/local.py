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

STATIC_ROOT = os.path.join(BASE_DIR, '/pos/static/')

INSTALLED_APPS += [
    'debug_toolbar',
]

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

print(FRESHBOOKS_CLIENT_ID)
print(FRESHBOOKS_CLIENT_SECRET)
print(FRESHBOOKS_REDIRECT_URI)