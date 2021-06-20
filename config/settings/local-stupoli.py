from .local import *
from .stupoli import *

# remove LocalMiddleware to allow us to see German translation
# in development. allow it in production in case someone wants
# to somehow specify a different language 
# https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#how-django-discovers-language-preference
MIDDLEWARE.remove('django.middleware.locale.LocaleMiddleware')

# uncomment below to enable English
# LANGUAGE_CODE = "en-us"