[![Build Status](https://travis-ci.org/SaturdayNeighborhoodHealthClinic/osler.svg?branch=master)](https://travis-ci.org/SaturdayNeighborhoodHealthClinic/osler)
[![codecov.io](https://codecov.io/github/SaturdayNeighborhoodHealthClinic/osler/coverage.svg?branch=master)](https://codecov.io/github/SaturdayNeighborhoodHealthClinic)

[![forthebadge](http://forthebadge.com/images/badges/powered-by-electricity.svg)](https://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/does-not-contain-treenuts.svg)](https://forthebadge.com)

# Osler

This is our osler project, which is a collection for all our
patient tracking. It's a django project.

You can check out a running demo at [oslerproject.org](http://oslerproject.org). The stack
for this implementation is nginx + gunicorn + sqlite on a smallest-possible DigitalOcean
droplet.

## Running locally

First, clone our repository

```bash
git clone https://github.com/SaturdayNeighborhoodHealthClinic/osler.git
```

First, get [pip](https://pip.pypa.io/en/stable/).

We also recommend running Osler in a virtual environment.
If you're going to run our project in a virtual env do th following:

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

Then use pip install our dependencies with:

```bash
pip install -r requirements.txt
```

(Python dependencies are stored in `requirements.txt`)

One of our dependencies is Pillow, which requires [some other libraries.](https://pillow.readthedocs.org/en/3.0.x/installation.html)

Once you've done that, *from the `osler/` build the test database with

```bash
sh scripts/reset_db.sh
```

This script is also used to rebuild the test database after making database
changes require migrations. Then, you can run the project in debug mode with

```bash
python manage.py runserver --settings osler.debug_settings
```

Once you have it running, you should be able to log into the debug database-backed
app with the user 'jrporter' with password 'password'.

## Deployment

There a lot of good resources that teach you how to deploy a django app, and there
are many ways to do it correctly. There's nothing too special about Osler in this regard!
However, we strongly recommmend [nginx, gunicorn, and postgres](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/).
