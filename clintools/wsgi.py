import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/washu/.virtualenvs/osler/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/washu/clintools')
sys.path.append('/home/washu/clintools/clintools')

os.environ['DJANGO_SETTINGS_MODULE'] = 'clintools.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/washu/.virtualenvs/osler/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.wsgi
application = django.core.wsgi.get_wsgi_application()
