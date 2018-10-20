from production_base import *

SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_URL = '/media'
SENDFILE_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media_auth/'
MEDIA_ROOT = SENDFILE_ROOT

# can has SSL?
# SECURE_SSL_REDIRECT = True

# override necessary until SSL implemented.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# TODO: configure url
ALLOWED_HOSTS = ['134.193.136.129']

DEFAULT_FROM_EMAIL = "webmaster@osler.umkc.edu"
SERVER_EMAIL = "admin@osler.umkc.edu"

# TODO: configure SMTP
EMAIL_HOST = "irony.wusm.wustl.edu"

ADMINS = (
    ('Artur Meller', 'ameller@wustl.edu'),
    ('Justin Porter', 'jrporter@wustl.edu'),
    ('Benji Katz', ' benjamin.katz@wustl.edu')
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'osler',
        'USER': 'django',
        'PASSWORD': DB_PASSWORD,
        'HOST': '134.193.138.85',
        'PORT': '',
    }
}
