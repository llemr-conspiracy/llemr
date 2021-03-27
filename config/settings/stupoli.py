# Custom settings for stupoli deploy
# -----------------------------------------------------------------------------
from .base import env

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

OSLER_DEFAULT_CITY = "Hamburg"
OSLER_DEFAULT_STATE = "Hamburg"
OSLER_DEFAULT_ZIP_CODE = "20459"
OSLER_DEFAULT_COUNTRY = "Deutschland"
OSLER_DEFAULT_ADDRESS = "Seewartenstraße 10"

OSLER_ABOUT_NAME = "Wiki"
OSLER_ABOUT_URL = env(
    "OSLER_ABOUT_URL",
    default="https://wiki.stupoli-hamburg.de",
)
