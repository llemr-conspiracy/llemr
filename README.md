# Osler

This is our clintools project, which is a collection for all our patient tracking and HPI-related web tools. It's a django project.

## Running locally

First, clone our repository

```
git clone https://github.com/SaturdayNeghborhoodHealthClinic/clintools.git
```

Then, make a file called `secret_key.txt` in the root directory of the project with a [django secret key](http://www.miniwebtool.com/django-secret-key-generator/). Since you're not using it in production, it doesn't really matter that you use it safely.

We store our project's dependencies in `requirements_file.txt`, so you should use [pip](https://pip.pypa.io/en/stable/) to install everything. We recommend running `clintools` in a virtual environment.
If you're going to run our project in a virtual env do th following:

```
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

Then install our dependencies with

```
pip install -r requirements.txt
```

Once you've done that, build the test database

```
python manage.py collectstatic
sh init_db.sh
```

(Alternatively, you can build a clean database by running ``./manage.py makemigrations && ./manage.py migrate``.)

Then, you can run the project with

```
python manage.py runserver
```
