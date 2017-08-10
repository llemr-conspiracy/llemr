from base_settings import *

DEBUG = True
CRISPY_FAIL_SILENTLY = not DEBUG
ALLOWED_HOSTS = []

SECRET_KEY = "^**4$36%t29#6+q4j9d3r$7da=i4*v398h%4k*mwc43pd1y#)u"

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'snhcwebtest@gmail.com'
EMAIL_HOST_PASSWORD = 'reallyjustatest'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
