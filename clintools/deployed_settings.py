from settings import *

DEBUG = TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['pttrack.snhc.wustl.edu']

with open(os.path.join(BASE_DIR, 'secrets/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

# TODO: change for deployment?
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}