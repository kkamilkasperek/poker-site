from django.conf.global_settings import CSRF_COOKIE_SECURE

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
DEBUG = False
ALLOWED_HOSTS = ['www.kamil123.tech']

# https
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# proxy headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED', 'https')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_ROOT = BASE_DIR / 'static'