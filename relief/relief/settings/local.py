from .base import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
# Set the DJNGO_SETTINGS_MODULE env var to project.settings.local to run production settings
DEBUG = True

ALLOWED_HOSTS = ['*']

STATIC_ROOT = os.path.join(BASE_DIR, '/pos/static/')