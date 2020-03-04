from deploy_settings import *

from getpass import getpass

DATABASES['default']['USER'] = 'root'
DATABASES['default']['PASSWORD'] = getpass()
