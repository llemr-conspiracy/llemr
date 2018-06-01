from osler.base_settings import *

DEBUG = True
CRISPY_FAIL_SILENTLY = not DEBUG
ALLOWED_HOSTS = []

SECRET_KEY = "^**4$36%t29#6+q4j9d3r$7da=i4*v398h%4k*mwc43pd1y#)u"

DEFAULT_FROM_EMAIL = "webmaster@osler.wustl.edu"
SERVER_EMAIL = "admin@osler.wustl.edu"
EMAIL_HOST = "irony.wusm.wustl.edu"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# add to tuple
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
