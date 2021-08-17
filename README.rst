LLEMR
=====

**L**\LEMR is a **L**\ightweight **E**\lectronic **M**\edical **R**\ecord.

A free, open-source EHR for free clinics.

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

.. image:: https://img.shields.io/badge/read-the%20docs-blue.svg
    :target: https://llemr.readthedocs.io/en/latest/
    :alt: Read the Docs


:License: GPLv3

Getting Started
---------------

* First, build the docker images with::

    $ docker-compose -f local.yml build

* To run the test server, then run::

    $ docker-compose -f local.yml up


For more info, have a look at the django-cookiecutter instructions for `running locally with Docker`_.

.. _`running locally with Docker`: https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html#getting-up-and-running-locally-with-docker

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have a working build of the docker containers::

  $ docker-compose -f local.yml run --rm django coverage run -m pytest


Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ docker-compose -f local.yml run --rm django coverage run -m pytest
    $ docker-compose -f local.yml run --rm django coverage html
    $ open htmlcov/index.html

Building Documentation
^^^^^^^^^^^^^^^^^^^^^^

Documentation can be built with::

	$ docker-compose -f local.yml up docs

Which serves documentation at `http://0.0.0.0:7000`

Deployment
----------

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html



