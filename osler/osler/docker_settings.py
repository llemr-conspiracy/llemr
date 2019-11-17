from .base_settings import *

DEBUG = TEMPLATE_DEBUG = os.environ.get('DJANGO_DEBUG', False)
CRISPY_FAIL_SILENTLY = not DEBUG

if not DEBUG:
    ALLOWED_HOSTS = ['localhost']

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = 'DENY'
else:
    ALLOWED_HOSTS = ['*']

with open(os.environ.get('DJANGO_SECRET_KEY_FILE')) as f:
    SECRET_KEY = f.read().strip()

SENDFILE_BACKEND = os.environ.get('DJANGO_SENDFILE_BACKEND')
SENDFILE_URL = os.environ.get('DJANGO_SENDFILE_URL')
SENDFILE_ROOT = os.environ.get('DJANGO_SENDFILE_ROOT')

MEDIA_URL = '/media_auth/'
MEDIA_ROOT = SENDFILE_ROOT


# one day in seconds
SESSION_COOKIE_AGE = 86400

# it would be nice to enable this, but we go w/o SSL from the WashU load
# balancer, meaning infinite redirects if we enable this :(
# SECURE_SSL_REDIRECT = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'osler_logger': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ.get('DJANGO_DEBUG_LOG_FILE'),
            'maxBytes': 1024 * 1024 * 30,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['osler_logger'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'osler': {
            'handlers': ['osler_logger'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

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

with open(os.environ.get('DATABASE_PASSWORD_FILE')) as f:
    DATABASE_PASSWORD = f.read().strip()

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_BACKEND'),
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}
