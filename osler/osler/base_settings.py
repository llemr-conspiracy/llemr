"""
Base django settings for osler.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
from __future__ import unicode_literals

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'followup',
    'workup',
    'demographics',
    'dashboard',
    'appointment',
    'referral',
    'api',
    'crispy_forms',
    'bootstrap3',
    'simple_history',
    'rest_framework',
    'audit',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'audit.middleware.AuditMiddleware'
)

ROOT_URLCONF = 'osler.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core/templates'),
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'osler.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'bg-danger',
    messages.WARNING: 'bg-warning',
    messages.INFO: 'bg-info',
    messages.SUCCESS: 'bg-success',
    messages.DEBUG: 'bg-primary',
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# for crispy_forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

INTERNAL_IPS = ('127.0.0.1',)  # used for debug toolbar

# Medical Settings
OSLER_MAX_SYSTOLIC = 400
OSLER_MIN_DIASTOLIC = 40

# Specifies which apps are displayed under action items on patient detail page
OSLER_TODO_LIST_MANAGERS = [
    ('core', 'ActionItem'),
    ('referral', 'FollowupRequest')]

OSLER_MAX_APPOINTMENTS = 5
OSLER_DEFAULT_APPOINTMENT_HOUR = 9

OSLER_WORKUP_COPY_FORWARD_FIELDS = ['PMH_PSH', 'fam_hx', 'soc_hx', 'meds',
                                    'allergies']
OSLER_WORKUP_COPY_FORWARD_MESSAGE = (u"Migrated from previous workup on {date}"
                                     u". Please delete this heading and modify"
                                     u" the following:\n\n{contents}")

# Dashboard settings
OSLER_CLINIC_DAYS_PER_PAGE = 20

OSLER_DEFAULT_DASHBOARD = 'home'
OSLER_PROVIDERTYPE_DASHBOARDS = {
    'Attending': 'dashboard-attending'
}

# List of IP addresses to exclude from audit
OSLER_AUDIT_BLACK_LIST = []
