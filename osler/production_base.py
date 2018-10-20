from osler.base_settings import *

with open(os.path.join(BASE_DIR, 'secrets/secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

DEBUG = TEMPLATE_DEBUG = False
CRISPY_FAIL_SILENTLY = not DEBUG


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

with open(os.path.join(BASE_DIR, 'secrets/database_password.txt')) as f:
    DB_PASSWORD = f.read().strip()
