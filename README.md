[![Circle CI](https://circleci.com/gh/SaturdayNeighborhoodHealthClinic/osler.svg?style=svg)](https://circleci.com/gh/SaturdayNeighborhoodHealthClinic/osler)
[![codecov.io](https://codecov.io/github/SaturdayNeighborhoodHealthClinic/osler/coverage.svg?branch=master)](https://codecov.io/github/SaturdayNeighborhoodHealthClinic)

# Osler

This is our osler project, which is a collection for all our
patient tracking. It's a django project.

## Running locally

First, clone our repository

```bash
git clone https://github.com/SaturdayNeighborhoodHealthClinic/osler.git
```

Next, get [pip](https://pip.pypa.io/en/stable/).

We also recommend running Osler in a virtual environment.
If you're going to run our project in a virtual env do th following:

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

Then use pip install our dependencies.

If you are trying to make a development build run:

```bash
pip install -r requirements-dev.txt
```

For a deployment build run:

```bash
pip install -r requirements.txt
```

(Python dependencies are stored in `requirements-dev.txt` for a development build and in `requirements.txt` for a deployment build)

One of our dependencies is Pillow, which requires [some other libraries.](https://pillow.readthedocs.org/en/3.0.x/installation.html)

Once you've done that, from the `osler/` build the test database with:

```bash
sh scripts/reset_db.sh
```
Windows users will need to use the batch file instead:
```bash
scripts/reset_db.bat
```

Windows users will need to use the batch file instead:
```bash
scripts/reset_db.bat
```

This script is also used to rebuild the test database after making database
changes require migrations. Then, you can run the project in debug mode with

```bash
python manage.py runserver --settings osler.debug_settings
```

Once you have it running, you should be able to log into the debug database-backed
app with the user 'jrporter' with password 'password'.

To run tests, run

```bash
python manage.py test
```

Remote servers without GUI access may need to [configure headless selenium](http://www.installationpage.com/selenium/how-to-run-selenium-headless-firefox-in-ubuntu/). A pretty good tutorial on doing this in the cloud is [here](http://jonathansoma.com/lede/algorithms-2017/servers/setting-up/).

## Deployment

There are a lot of good resources that teach you how to deploy a django app, and there
are many ways to do it correctly. There's nothing too special about Osler in this regard!
However, we strongly recommmend [nginx, gunicorn, and postgres](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/).
