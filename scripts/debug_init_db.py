'''
This script builds the additonal entries in the database that are not built
into a deployment database. Fake patients, possibly fake providers, etc.

scripts/init_db.py contains data that is real and should be used in a
deployment environment. This script relies on model entries created by that
script.
'''

from django.contrib.auth.models import User
from pttrack import models
from 
from datetime import date

# pylint: disable=invalid-name

user = User.objects.create_superuser('jrporter', 'justinrporter@wustl.edu',
                                     'password')
user.first_name = "Justin"
user.last_name = "Porter"
user.save()

user = User.objects.create_user('rjain', 'jainr@wusm.wustl.edu',
                                'password')
user.first_name = "Radhika"
user.last_name = "Jain"
user.save()

p = models.Patient(first_name="Tommy",
                   middle_name="Lee",
                   last_name="Jones",
                   address="123 Drury Ln.",
                   zip_code="63108",
                   date_of_birth=date(year=1962,month=2,day=1),
                   phone="425-243-9115",
                   gender=models.Gender.objects.all()[0])
p.save()
p.languages.add(models.Language.objects.all()[0])
p.ethnicities.add(models.Ethnicity.objects.all()[0])






q = models.Patient(first_name="Frankie",
                   middle_name="Lane",
                   last_name="McNath",
                   address="6310 Scott Ave.",
                   zip_code="63110",
                   date_of_birth=date(year=1989,month=8,day=9),
                   phone="501-233-1234",
                   gender=models.Gender.objects.all()[0])
q.save()
q.languages.add(models.Language.objects.all()[0])
q.ethnicities.add(models.Ethnicity.objects.all()[0])

print "Done!"
