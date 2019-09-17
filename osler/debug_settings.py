from osler.base_settings import *

INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)

DEBUG = True
CRISPY_FAIL_SILENTLY = not DEBUG
ALLOWED_HOSTS = []

SECRET_KEY = "^**4$36%t29#6+q4j9d3r$7da=i4*v398h%4k*mwc43pd1y#)u"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MIDDLEWARE = MIDDLEWARE + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

DEFAULT_FROM_EMAIL = "webmaster@osler.wustl.edu"
SERVER_EMAIL = "admin@osler.wustl.edu"
EMAIL_HOST = "irony.wusm.wustl.edu"
ADMINS = (
    ('Tech Tzar', 'techtzar@wustl.edu'),
)
