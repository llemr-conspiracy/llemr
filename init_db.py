from pttrack import models
from datetime import date

l = models.Language(name="English")
l.save()

e = models.Ethnicity(name="White")
e.save()

for lname in ["Male", "Female"]:
    g = models.Gender(long_name=lname, short_name=lname[0])
    g.save()


p = models.Provider(first_name="Tommy",
                    middle_name="Lee",
                    last_name="Jones",
                    phone="425-243-9115",
                    gender=models.Gender.objects.all()[0],
                    email="tljones@wustl.edu",
                    )
p.save()

p = models.Patient(first_name="Frankie",
                   middle_name="Lane",
                   last_name="McNath",
                   address="6310 Scott Ave.",
                   date_of_birth=date(year=1989,
                                      month=8,
                                      day=9),
                   phone="501-233-1234",                   
                   language=l,
                   ethnicity=e,
                   gender=models.Gender.objects.all()[0])
p.save()

for lname in ["Attending Physician",
              "Preclinical Medical Student",
              "Clinical Medical Student",
              "Coordinator"]:
    p = models.ProviderType(long_name=lname, short_name=lname.split()[0])
    p.save()
    
for clintype in ["Basic Care Clinic", "Depression & Anxiety Clinic", "Dermatology", "Muscle and Joint Pain"]:
    t = models.ClinicType(name=clintype)
    t.save()

i = models.ActionInstruction(instruction="Vaccine Followup")
i.save()
