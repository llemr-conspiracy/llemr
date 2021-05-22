from .local import *
from .stupoli import *

# remove LocalMiddleware to allow us to see German translation
# in development. allow it in production in case someone wants
# to somehow specify a different language 
# https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#how-django-discovers-language-preference
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'simple_history.middleware.HistoryRequestMiddleware',
    'osler.audit.middleware.AuditMiddleware'
]

# uncomment below to enable English
# LANGUAGE_CODE = "en-us"