Running LLEMR in Production
===========================


Building Production Containers
--------------------------

The production containers of LLEMR are slightly different than their development counterparts, and require a few extra steps to run. It is recommended to remove the local containers before continuing to prevent conflicts or confusion. This guide will use the generic production.yml docker-compose stack, but it is recommend to copy and customize it to your use case.

Install Docker per the Docker instructions for your platform.
--------------------------------------------------------------


Download the `latest release of LLEMR <https://github.com/llemr-conspiracy/llemr/releases/latest>`_

https://github.com/llemr-conspiracy/llemr
-----------------------------------------------------------------------------------------------------------------
  Via git:

.. code-block:: console

	$ git clone https://github.com/llemr-conspiracy/llemr.git
  $ git checkout v2.2.0

As a zip:

.. code-block:: console

	$ wget https://github.com/llemr-conspiracy/llemr/archive/refs/tags/v2.2.0.tar.gz
	$ tar -xvzf v2.2.0.tar.gz

Set up a docker compose file
----------------------------

The global configuration of your docker containers is set up in `production.yml`.
We have a number of examples, including the demo (`production-demo.yml`). These set up virtual machines for each of the elements of the web app.

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
        - ./.envs/.production/.secrets
      networks:
        - database_network

The key here is the `env_file` section, which sets some important environment variables. the file `./.envs/.production/.secrets` *does not exist*, and must be created. Create a file that looks something like:


Create the :code:`.secrets` file:
----------------------------------
	This file contains sensitive information about the LLEMR instance that would allow break confidentailty if exposed. As such, it must be created manually for each unique LLEMR instance. It should never be check into git, and is ignored by git by default. The file must be placed in :code:`osler/.envs/.production/.secrets`.
	The file should contain database credentials and the django secret key. **Do not use the values below. They are only an example**

	.. code-block::

		# PostgreSQL
		# ------------------------------------------------------------------------------
		POSTGRES_HOST=postgres
		POSTGRES_PORT=5432
		POSTGRES_DB=llemr
		POSTGRES_USER=BnnIJhssshZrnURWgfjnnEXZRMzhNZCx
		POSTGRES_PASSWORD=JzQ6eHA47iiEzURQo1xJ2VPeGpRY81edS1UpuQc82KP5bb7T8t6qR7ANFTRK5bxI


		# Django
		# ------------------------------------------------------------------------------
		DJANGO_SECRET_KEY=PbQjPuCXmpX4dHJITSI2nSJy6lzivrHkyxIZJkAnowUsEzsWkucovzd75yz8BqVH

  The django secret key can be generated with the command :code:`python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`, while you can use any preferred method to choose your postgres username and password.


The Web App
-----------

The web app is run with gunicorn in a custom Dockerfile. This guy accounts for by far the majority of the runtime of `docker-compose build`.

.. code-block:: yaml

  django:
    build:
      context: .
      dockerfile: ./compose/production/django/Dockerfile
    image: llemr_production_django
    depends_on:
      - postgres
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.demo
    env_file:
      - ./.envs/.production/.django
      - ./.envs/.production/.secrets
    command: /start
    volumes:
      - production_static_files:/app/staticfiles
    networks:
      - nginx_network
      - database_network

Notice that we use the `environment` section to provide `DJANGO_SETTINGS_MODULE`, which points to `config/settings/demo.py`. This file contains:

.. code-block:: python

    from .production import *

Thus, it inherits the configurations listed in `config/settings/production.py`, and then overrides anything in `production.py`. Most of the settings in `production.py` are strong recommendations for production, whereas those in `demo.py` are likely to be configured by you.

.. code-block:: python

    from .production import *

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
    OSLER_DISPLAY_DIAGNOSIS = True
    OSLER_DISPLAY_VOUCHERS = False
    OSLER_DISPLAY_WILL_RETURN = False
    OSLER_DISPLAY_ATTENDANCE = False
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
    build: ./compose/production/nginx
    ports:
      - 80:80
      - 443:443
    depends_on:
      - django
    volumes:
      - production_static_files:/app/staticfiles
    networks:
      - nginx_network


Generate or install TLS keys:
--------------------------------
In production, LLEMR should always be accessed exclusivly with HTTPS for security reasons. In the production compose stack, nginx automatically serves LLEMR using HTTPS with the SSL certificates at `osler/compose/production/certs/`. If you are using certificates issued by a third party, place them in this directory, ensuring the following permissions

.. code-block::

	-rw-r--r-- cert.crt
	-rw------- cert.key

Alternatively, you can generate your own certificates for nginx to use. Because these will be self-signed, they will cause all web browers to display a certificate warning the first time vising the site.
To generate certificates, run this from the root directory of LLEMR:

.. code-block:: console

	openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout ./compose/production/nginx/certs/cert.key -out ./compose/production/nginx/certs/cert.crt

Build and run the docker containers 
------------------------------------
This could take a while. Note: if you redo any previous steps, rerun this command with the :code:`--build` argument.

.. code-block:: console

	$ docker-compose -f production.yml up


Check everything is working by visiting https://localhost:80 in your browser.