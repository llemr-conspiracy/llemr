'''
This script builds the additonal entries in the database that are not built
into a deployment database. Fake patients, possibly fake providers, etc.

scripts/init_db.py contains data that is real and should be used in a
deployment environment. This script relies on model entries created by that
script.
'''

from django.contrib.auth.models import User
from pttrack import models
from datetime import date
import pandas
import random
import numpy
# pylint: disable=invalid-name

numpy.warnings.filterwarnings('ignore')

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


df = pandas.read_csv("TestDatabaseFiller.csv")
malenames = df.Male_First_Name
femalesnames = df.Female_First_Name
lastnames = df.Last_Name
streetnames = df.Street_Name
for i in xrange(0,250):
      a = models.Patient(first_name=malenames[random.randint(0,99)],
                        middle_name="",
                        last_name=lastnames[random.randint(0,399)],
                        address=streetnames[random.randint(0,499)],
                        zip_code=str(random.randint(63101,63110)),
                        date_of_birth=date(year=random.randint(1950,2000),month=random.randint(1,12),day=random.randint(1,28)),
                        phone="314-555-"+str(random.randint(1000,9999)),
                        gender=models.Gender.objects.all()[0])
      a.save()





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
