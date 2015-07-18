from settings import *

DEBUG = TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['pttrack.snhc.wustl.edu']

with open(os.path.join(BASE_DIR, 'secrets/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# TODO: change for deployment?
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}