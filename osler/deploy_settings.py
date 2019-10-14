from base_settings import *

DEBUG = TEMPLATE_DEBUG = False
CRISPY_FAIL_SILENTLY = not DEBUG
ALLOWED_HOSTS = ['osler.wustl.edu']

with open(os.path.join(BASE_DIR, 'secrets/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

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

DEFAULT_FROM_EMAIL = "webmaster@osler.wustl.edu"
SERVER_EMAIL = "admin@osler.wustl.edu"
EMAIL_HOST = "irony.wusm.wustl.edu"
ADMINS = (
    ('Artur Meller', 'ameller@wustl.edu'),
    ('Justin Porter', 'jrporter@wustl.edu'),
)

with open(os.path.join(BASE_DIR, 'secrets/database_password.txt')) as f:
    DB_PASSWORD = f.read().strip()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'osler',
        'USER': 'django',
        'PASSWORD': DB_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
    }
}
