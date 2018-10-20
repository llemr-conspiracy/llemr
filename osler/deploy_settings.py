from osler.production_base import *

ALLOWED_HOSTS = ['osler.wustl.edu']

# it would be nice to enable this, but we go w/o SSL from the WashU load
# balancer, meaning infinite redirects if we enable this :(
# SECURE_SSL_REDIRECT = True

DEFAULT_FROM_EMAIL = "webmaster@osler.wustl.edu"
SERVER_EMAIL = "admin@osler.wustl.edu"
EMAIL_HOST = "irony.wusm.wustl.edu"
ADMINS = (
    ('Artur Meller', 'ameller@wustl.edu'),
    ('Justin Porter', 'jrporter@wustl.edu'),
    ('Benji Katz', 'benjamin.katz@wustl.edu')
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'osler',
        'USER': 'django',
        'PASSWORD': DB_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
