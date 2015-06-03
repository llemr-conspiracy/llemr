# SNHC clintools

This is our clintools project, which is a collection for all our patient tracking and HPI-related web tools. It's a django project.

## Running locally

First, clone our repository

```
git clone https://github.com/SaturdayNeghborhoodHealthClinic/clintools.git
```

Then, make a file called `secret_key.txt` in the root directory of the project with a [django secret key](http://www.miniwebtool.com/django-secret-key-generator/). Since you're not using it in production, it doesn't really matter that you use it safely.

You'll also need to install [djangular](http://django-angular.readthedocs.org/en/latest/installation.html) and [django-bootstrap3](http://django-bootstrap3.readthedocs.org/en/latest/)

```
pip install django-angular
pip install django-bootstrap3
```

then, run

```
python manage.py collectstatic
```

Once you've done that, build the database

```
python manage.py makemigrations pttrack
python manage.py migrate
```

Then, you can run the project with

```
python manage.py runserver
```
