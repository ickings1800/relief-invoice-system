from .base import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
# Set the DJANGO_SETTINGS_MODULE env var to project.settings.production to run production settings
DEBUG = False

ALLOWED_HOSTS = ['localhost']

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')