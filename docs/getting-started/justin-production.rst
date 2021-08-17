Running in Production
====================================

Set up a docker compose file
----------------------------

The global configuration of your docker compose swarm is set up in `production.yml`.
We have a number of examples, including the demo (`production-demo.yml`). These set up
virtual machines for each of the elements of the web app.

The Database
------------

We use PostgresQL. The database container is named `postgres`. Here is an example of a configuration:

.. code-block:: yaml

    postgres:
      build:
        context: .
        dockerfile: ./compose/production/postgres/Dockerfile
      image: llemr_production_postgres
      container_name: postgres
      volumes:
        - production_postgres_data:/var/lib/postgresql/data
        - production_postgres_data_backups:/backups
      env_file:
        - ./.envs/.production/.postgres
        - ./.envs/.secrets/.postgres
      networks:
        - database_network

The key here is the `env_file` section, which sets some important environment variables:

.. code-block:: bash

    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432
    POSTGRES_DB=llemr
    POSTGRES_USER=django

Furthermore, the file `./.envs/.secrets/.postgres` *does not exist*, and must be created. Create a file that looks something like:

.. code-block:: bash

    POSTGRES_PASSWORD=FybL7H4ftzJPiEWQrWMDuogLUcLgv47iw78vUqHexPPnJGd9EJDPeDXH9RGdiTBC


.. warning::
    POSTGRES_PASSWORD is **priviledged information** and should be kept secret. Do not check it in to your git repository. The string provided here is an example--do not use it yourself! Generate a long, random string yourself and use it instead. 


The Web App
-----------

The web app is run with gunicorn in a custom Dockerfile. This guy accounts for by far the majority of the runtime of `docker-compose build`.

.. note::
    We provide the postgres configuration environment files
    (`.envs/.production/.postgres` and `./.envs/.secrets/.postgres`) to _both_
    the django container and the postgres container. This is because the 
    django container needs to be able to connect and authenticate to the 
    postgres container!

.. code-block:: yaml

    django:
      build:
        context: .
        dockerfile: ./compose/production/django/Dockerfile
      image: llemr_production_django
      container_name: django
      ports:
        - 5000:5000
      depends_on:
        - postgres
        - redis
      environment:
        - DJANGO_SETTINGS_MODULE=config.settings.production-demo
      env_file:
        - ./.envs/.production/.django
        - ./.envs/.production/.postgres
        - ./.envs/.secrets/.postgres
        - ./.envs/.secrets/.django
      command: /start
      networks:
        - nginx_network
        - database_network

Notice that we use the `environment` section to provide `DJANGO_SETTINGS_MODULE`, which points to `config/settings/production-demo.py`. This file contains:

.. code-block:: python

    from .production import *
    from .demo import *

Thus, it combines the configurations listed in `config/settings/production.py` and `config/settings/demo.py`, with those in `demo.py` overriding anything in `production.py` (since `demo.py` comes second). Most of the settings in `production.py` are strong recommendations for production, whereas those in `demo.py` are likely to be configured by you.

.. code-block:: python
    from .base import env

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


The Web Server
--------------

The web server we use is nginx. It's responsible for serving static files, terminating SSL, and passing data to gunicorn. The pertinent part of the docker compose file is here:

.. code-block:: yaml

    nginx:
      image: nginx:1.19
      container_name: nginx
      ports:
        - 80:80
        - 443:443
      env_file:
        - ./.envs/.production/.nginx
      volumes:
        - ./compose/production/nginx/templates:/etc/nginx/templates
        - ./compose/production/nginx/certs:/etc/nginx/certs
      depends_on:
        - django
      networks:
        - nginx_network

To get this working, you need to put an SSL certificate named `cert.crt` in `compose/production/nginx/certs`. SSL certificates get kind of complicated, but you can usually get one from Let's Encrypt (https://letsencrypt.org/) or, if you're part of an organization with an IT department like a university, you can ask your friendly local IT professional. In a pinch, just to get things running, you can make a self-signed one like so:

.. code-block:: console

    $ mkdir -p ./compose/production/nginx/certs
    $ openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout ./compose/production/nginx/certs/cert.key -out ./compose/production/nginx/certs/cert.crt