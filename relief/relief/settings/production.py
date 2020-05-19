from .base import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

#CSRF_COOKIE_SECURE = True

#SESSION_COOKIE_SECURE = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
print(STATIC_ROOT)
