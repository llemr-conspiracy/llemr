"""
WSGI config for osler when DJANGO_SETTINGS_MODULE is an environment var.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.get("DJANGO_SETTINGS_MODULE")
application = get_wsgi_application()
