from base_settings import *

DEBUG = TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['pttrack.snhc.wustl.edu']

with open(os.path.join(BASE_DIR, 'secrets/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# it would be nice to enable this, but we go w/o SSL from the WashU load
# balancer, meaning infinite redirects if we enable this :(
# SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

with open(os.path.join(BASE_DIR, 'secrets/database_password.txt')) as f:
    DB_PASSWORD = f.read().strip()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'osler',
        'USER': 'django',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}