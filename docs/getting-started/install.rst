Installation
============


Basic (Local) Installation
--------------------------

#. Install Docker_ per the Docker instructions for your platform.

#. Download the `latest release of LLEMR <https://github.com/llemr-conspiracy/llemr/releases/latest>`_ either with git:

	.. code-block:: console

		$ git clone https://github.com/llemr-conspiracy/llemr.git
		$ git checkout v2.1.0

	or as a zip:

	.. code-block:: console

		$ wget https://github.com/llemr-conspiracy/llemr/archive/refs/tags/v2.1.0.tar.gz
		$ tar -xvzf v2.1.0.tar.gz

#. Build the docker containers (this could take a while):

    .. code-block:: console

    	$ docker compose -f local.yml build

#. Create a superuser for yourself:

	.. code-block:: console

		$ docker-compose -f local.yml run --rm django python manage.py createsuperuser
		Starting postgres         ... done
		Creating osler_django_run ... done
		PostgreSQL is available
		Username: osleruser
		Email address: contact@oslerproject.net
		Password:
		Password (again):
		Superuser created successfully.

#. Run the docker containers

	.. code-block:: console

		$ docker-compose -f local.yml up
		[...]
		django      | Django version 3.2.10, using settings 'config.settings.local'
		django      | Development server is running at http://0.0.0.0:8000/
		django      | Using the Werkzeug debugger (http://werkzeug.pocoo.org/)
		django      | Quit the server with CONTROL-C.

#. Visit the development URL (http://0.0.0.0:8000/) in the browser

Production Installation
-----------------------

As above, except use a production Docker compose file for all `docker-compose` invocations.

.. code-block:: console

	$ docker compose -f production.yml build
	$ docker compose -f production.yml run --rm django python manage.py createsuperuser
	$ docker compose -f production.yml up


.. _Docker: https://docs.docker.com/get-docker/
