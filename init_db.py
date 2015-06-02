from pttrack import models

l = models.Language(name="English")
l.save()

e = models.Ethnicity(name="White")
e.save()

for lname in ["Male", "Female"]:
    g = models.Gender(long_name=lname, short_name=lname[0])
    g.save()

for lname in ["Attending Physician",
              "Preclinical Medical Student",
              "Clinical Medical Student",
              "Coordinator"]:
    p = models.ProviderType(long_name=lname, short_name=lname.split()[0])
    p.save()
    
for clintype in ["Basic Care Clinic", "Depression & Anxiety Clinic", "Dermatology", "Muscle and Joint Pain"]:
    t = models.ClinicType(name=clintype)
    t.save()
