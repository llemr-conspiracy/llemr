# Custom settings for umkc deploy
# -----------------------------------------------------------------------------
from .base import env

OSLER_ROLE_DASHBOARDS = {
    'Attending': 'dashboard-attending',
    'Physician': 'dashboard-attending',
}

# overrides ./.envs/.production/.django to add mystery IP address
ALLOWED_HOSTS = ['osler.umkc.edu', '134.193.143.63']

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'remote.med.umkc.edu@umkc.edu'
EMAIL_HOST = 'massmail.umsystem.edu'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

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

OSLER_DEFAULT_CITY = "Kansas City"
OSLER_DEFAULT_STATE = "MO"
OSLER_DEFAULT_ZIP_CODE = "64109"
OSLER_DEFAULT_COUNTRY = "USA"
OSLER_DEFAULT_ADDRESS = "3151 Olive St"

OSLER_ABOUT_NAME = "Help"
OSLER_ABOUT_URL = "http://www.sojournerhealthclinic.com/?page_id=1755"

# Default Encounter Status
OSLER_DEFAULT_ACTIVE_STATUS = ('Present', True)
OSLER_DEFAULT_INACTIVE_STATUS = ('Inactive', False)
