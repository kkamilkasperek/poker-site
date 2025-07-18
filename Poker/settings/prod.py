from django.conf.global_settings import CSRF_COOKIE_SECURE

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
DEBUG = False
ALLOWED_HOSTS = ['kamil123.tech' ,'www.kamil123.tech']

# https
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# proxy headers (for now http is accepted as secure)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_ROOT = BASE_DIR / 'static'