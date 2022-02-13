
from .production import *

# Dont bother with REDIS for demo
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# Use django default static storage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

TIME_ZONE = "America/Chicago"
LANGUAGE_CODE = "en-us"

OSLER_ROLE_DASHBOARDS = {
    'Attending': 'dashboard-attending',
    'Physician': 'dashboard-attending',
}

OSLER_DISPLAY_REFERRALS = False
OSLER_DISPLAY_APPOINTMENTS = False
OSLER_DISPLAY_CASE_MANAGERS = False
OSLER_DISPLAY_ATTESTABLE_BASIC_NOTE = False
OSLER_DISPLAY_DIAGNOSIS = False
OSLER_DISPLAY_VOUCHERS = False
OSLER_DISPLAY_WILL_RETURN = False
OSLER_DISPLAY_ATTENDANCE = True
OSLER_DISPLAY_FOLLOWUP = False
OSLER_DISPLAY_VACCINE = False

OSLER_DEFAULT_CITY = "Gotham"
OSLER_DEFAULT_STATE = "New Jersey"
OSLER_DEFAULT_ZIP_CODE = "00000"
OSLER_DEFAULT_COUNTRY = "USA"
OSLER_DEFAULT_ADDRESS = ""

OSLER_ABOUT_NAME = "About"
OSLER_ABOUT_URL = "https://llemrconspiracy.org"
