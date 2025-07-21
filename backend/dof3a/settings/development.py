from .common import *

SECRET_KEY = 'django-insecure-(y)t(l%6$u8qgqwk-4uee4*29j@_oi^npr#jjw9*^8t*eodnch'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]
