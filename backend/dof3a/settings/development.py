from .common import *

SECRET_KEY = 'django-insecure-(y)t(l%6$u8qgqwk-4uee4*29j@_oi^npr#jjw9*^8t*eodnch'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dofaa_db',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '09dne1!!jkl-rootpassword'
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]
