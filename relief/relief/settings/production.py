from .base import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
print("------------------ PRODUCTION -----------------")
DEBUG = False

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'debug.log'),
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/app/relief.sqlite'
    }
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')

STATIC_ROOT = BASE_DIR / 'staticfiles'
print("PRODUCTION STATIC ROOT:: ", STATIC_ROOT)
