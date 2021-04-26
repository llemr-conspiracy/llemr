Running Osler in Production
===========================


Building Production Containers
--------------------------

The production containers of Osler are slightly different than their development counterparts, and require a few extra steps to run. It is recommended to remove the local containers before continuing to prevent conflicts or confusion. This guide will use the generic production.yml docker-compose stack, but it is recommend to copy and customize it to your use case.

#. Install Docker_ per the Docker instructions for your platform.

#. Download the `latest release of Osler <https://github.com/oslerproject/osler/releases/latest>`_ either with git:

	.. code-block:: console

		$ git clone https://github.com/oslerproject/osler.git
		$ git checkout v2.1.0

	or as a zip:

	.. code-block:: console

		$ wget https://github.com/oslerproject/osler/archive/v2.1.0.tar.gz
		$ tar -xvzf v2.1.0.tar.gz

#. Create the :code:`.secrets` file:
	This file contains sensitive information about the Osler instance that would allow break confidentailty if exposed. As such, it must be created manually for each unique Osler instance. The file must be placed in :code:`osler/.envs/.production/.secrets`.
	The file should contain database credentials and the django secret key. **Do not use the values below. They are only an example**

	.. code-block::

		# PostgreSQL
		# ------------------------------------------------------------------------------
		POSTGRES_HOST=postgres
		POSTGRES_PORT=5432
		POSTGRES_DB=osler
		POSTGRES_USER=BnnIJhssshZrnURWgfjnnEXZRMzhNZCx
		POSTGRES_PASSWORD=JzQ6eHA47iiEzURQo1xJ2VPeGpRY81edS1UpuQc82KP5bb7T8t6qR7ANFTRK5bxI


		# Django
		# ------------------------------------------------------------------------------
		DJANGO_SECRET_KEY=PbQjPuCXmpX4dHJITSI2nSJy6lzivrHkyxIZJkAnowUsEzsWkucovzd75yz8BqVH

#. Generate or install TLS keys:
	In production, Osler should always be accessed exclusivly with HTTPS for security reasons. In the production compose stack, nginx automatically serves Osler using HTTPS with the SSL certificates at `osler/compose/production/certs/`. If you are using certificates issued by a third party, place them in this directory, ensuring the following permissions
	.. code-block::
		-rw-r--r-- cert.crt
		-rw------- cert.key
	Alternatively, you can generate your own certificates for nginx to use. Because these will be self-signed, they will cause all web browers to display a certificate warning the first time vising the site.
	To generate certificates, run this from the root directory of Osler:

	.. code-block:: console

		openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout ./compose/production/nginx/certs/cert.key -out ./compose/production/nginx/certs/cert.crt

#. Build and run the docker containers (this could take a while). Note: if you redo any previous steps, rerun this command with the :code:`--build` argument.
    .. code-block:: console

    	$ docker-compose -f production.yml up


#. Check everything is working by visiting https://localhost in your browser.