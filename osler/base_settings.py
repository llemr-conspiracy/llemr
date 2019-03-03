"""
Base django settings for osler.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

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
    'pttrack',
    'followup',
    'workup',
    'demographics',
    'appointment',
    'referral',
    'api',
    'crispy_forms',
    'bootstrap3',
    'bootstrap3_datetime',
    'simple_history',
    'rest_framework',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
)

ROOT_URLCONF = 'osler.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'pttrack/templates'),
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# for crispy_forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

INTERNAL_IPS = ('127.0.0.1',)  # used for debug toolbar

# Medical Settings
OSLER_MAX_SYSTOLIC = 400
OSLER_MIN_DIASTOLIC = 40

# Specifies which apps are displayed under action items on patient detail page
OSLER_TODO_LIST_MANAGERS = [
    ('pttrack', 'ActionItem'),
    ('referral', 'FollowupRequest')]

OSLER_MAX_APPOINTMENTS = 5
OSLER_DEFAULT_APPOINTMENT_HOUR = 9

OSLER_WORKUP_COPY_FORWARD_FIELDS = ['PMH_PSH', 'fam_hx', 'soc_hx', 'meds',
                                    'allergies']
OSLER_WORKUP_COPY_FORWARD_MESSAGE = (u"Migrated from previous workup on {date}"
                                     u". Please delete this heading and modify"
                                     u" the following:\n\n{contents}")
