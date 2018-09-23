from base_settings import *

DEBUG = TEMPLATE_DEBUG = False
CRISPY_FAIL_SILENTLY = not DEBUG

ALLOWED_HOSTS = ['localhost']

with open(os.path.join(BASE_DIR, 'secrets/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

SENDFILE_BACKEND = os.environ.get('DJANGO_SENDFILE_BACKEND')
SENDFILE_URL = os.environ.get('DJANGO_SENDFILE_URL')
SENDFILE_ROOT = os.environ.get('DJANGO_SENDFILE_ROOT')

MEDIA_URL = '/media_auth/'
MEDIA_ROOT = SENDFILE_ROOT

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# one day in seconds
SESSION_COOKIE_AGE = 86400

# it would be nice to enable this, but we go w/o SSL from the WashU load
# balancer, meaning infinite redirects if we enable this :(
# SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# DEFAULT_FROM_EMAIL = "webmaster@osler.wustl.edu"
# SERVER_EMAIL = "admin@osler.wustl.edu"
# EMAIL_HOST = "irony.wusm.wustl.edu"
# ADMINS = (
#     ('Artur Meller', 'ameller@wustl.edu'),
#     ('Justin Porter', 'jrporter@wustl.edu'),
#     ('Nicolas Ledru', 'nicolas.ledru@wustl.edu'),
#     ('Arjav Shah', 'arjav.shah@wustl.edu'),
#     ('Benji Katz','benjamin.katz@wustl.edu')
# )

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_BACKEND'),
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}
