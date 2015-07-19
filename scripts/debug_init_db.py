import init_db

from django.contrib.auth.models import User

user = User.objects.create_user('jrporter', 'justinrporter@wustl.edu',
                                'password')
user.first_name = "Justin"
user.last_name = "Porter"
user.save()

user = User.objects.create_user('rjain', 'jainr@wusm.wustl.edu',
                                'password')
user.first_name = "Radhika"
user.last_name = "Jain"
user.save()

# p = models.Provider(first_name="Tommy",
#                     middle_name="Lee",
#                     last_name="Jones",
#                     phone="425-243-9115",
#                     gender=models.Gender.objects.all()[0],
#                     can_attend=True,
#                     # associated_user=user)
#                     )
# p.save()


p = models.Patient(first_name="Frankie",
                   middle_name="Lane",
                   last_name="McNath",
                   address="6310 Scott Ave.",
                   date_of_birth=date(year=1989,
                                      month=8,
                                      day=9),
                   phone="501-233-1234",
                   gender=models.Gender.objects.all()[0])
p.save()
p.languages.add(l)
p.ethnicities.add(e)

print "Done!"
