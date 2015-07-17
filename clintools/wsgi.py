import os
import sys
import site

# pylint: disable=invalid-name

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_DIR = os.path.expanduser("~")

# Add the app's directory to the PYTHONPATH
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'clintools'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'clintools.settings'

try:
    # If you have everything installed globally, it should Just Work (TM)

    import django.core.wsgi
    application = django.core.wsgi.get_wsgi_application()
except ImportError:
    # If we fail to import django.core.wsgi, then we maybe don't have stuff
    # installed locally and we should look for a virtualenv

    VENV_NAME = "osler"
    VENV_DIR = os.path.join(HOME_DIR, '.virtualenvs/', VENV_NAME)

    # Add the site-packages of the chosen virtualenv to work with
    site.addsitedir(os.path.join(VENV_DIR,
                                 '/local/lib/python2.7/site-packages'))

    # Activate your virtual env
    activate_env = os.path.expanduser(
        os.path.join(VENV_DIR, "/bin/activate_this.py"))
    execfile(activate_env, dict(__file__=activate_env))

    import django.core.wsgi
    application = django.core.wsgi.get_wsgi_application()
