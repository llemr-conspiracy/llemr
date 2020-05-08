from __future__ import unicode_literals
from past.builtins import execfile
from builtins import range
import os
import sys
import site

# pylint: disable=invalid-name


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the app's directory to the PYTHONPATH
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'osler'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'osler.deploy_settings'

os.environ['PYTHONHASHSEED'] = 'random'

try:
    # If you have everything installed globally, it should Just Work (TM)

    import django.core.wsgi
    from django.contrib.auth.handlers.modwsgi import check_password

    application = django.core.wsgi.get_wsgi_application()
except ImportError:
    # If we fail to import django.core.wsgi, then we maybe don't have stuff
    # installed locally and we should look for a virtualenv
    VENVS_DIRNAME = '.virtualenvs'

    pdirs = os.path.split(BASE_DIR)

    # search every directory along the way to this directory for
    # VENVS_DIRNAME, where we expect the virtualenvs to be stored.
    # we don't need to search the first directory, since that is
    # usually /home/ and having only one arg to os.path.join is bad
    for pdir in [os.path.join(*pdirs[0:i])
                 for i in range(1, len(pdirs))]:
        if VENVS_DIRNAME in os.listdir(pdir):
            HOME_DIR = pdir
            break

    assert HOME_DIR in BASE_DIR

    VENV_NAME = "osler"
    VENV_DIR = os.path.join(HOME_DIR, VENVS_DIRNAME, VENV_NAME)

    # Add the site-packages of the chosen virtualenv to work with
    site.addsitedir(os.path.join(VENV_DIR,
                                 '/local/lib/python2.7/site-packages'))

    # Activate your virtual env
    activate_env = os.path.join(VENV_DIR, "bin/activate_this.py")

    assert os.path.isfile(activate_env)

    execfile(activate_env, dict(__file__=activate_env))

    import django
    django.setup()

    import django.core.wsgi
    from django.contrib.auth.handlers.modwsgi import check_password

    application = django.core.wsgi.get_wsgi_application()
