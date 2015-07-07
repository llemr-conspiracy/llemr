from pttrack import models
from pttrack import followup_models
from datetime import date

for lang_name in ["Arabic", "Armenian", "Bengali", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Finnish", "French", "French Creole", "German", "Greek", "Hebrew", "Hindi/Urdu", "Hungarian", "Italian", "Japanese", "Korean", "Lithuanian", "Persian", "Polish", "Portuguese", "Romanian", "Russian", "Samoan", "Serbocroatian", "Slovak", "Spanish", "Swedish", "Tagalog", "Thai/Laotian", "Turkish", "Ukrainian", "Vietnamese", "Yiddish"]:
    l = models.Language(name=lang_name)
    l.save()

for ethnic_name in ["American Indian or Alaska Native", "Asian", "Black or African American", "Hispanic or Latino", "Native Hawaiian or Other Pacific Islander", "White"] 
    e = models.Ethnicity(name=ethnic_name)
    e.save()

for lname in ["Male", "Female", "Other"]:
    g = models.Gender(long_name=lname, short_name=lname[0])
    g.save()


p = models.Provider(first_name="Tommy",
                    middle_name="Lee",
                    last_name="Jones",
                    phone="425-243-9115",
                    gender=models.Gender.objects.all()[0],
                    email="tljones@wustl.edu",
                    can_attend=True,
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

for clintype in ["Basic Care Clinic", "Depression & Anxiety Clinic",
                 "Dermatology Clinic", "Muscle and Joint Pain Clinic"]:
    t = models.ClinicType(name=clintype)
    t.save()

for ai_type in ["Vaccine Reminder", "Lab Follow-Up", "PCP Follow-Up", "Other"]:
    i = models.ActionInstruction(instruction=ai_type)
    i.save()

for contact_method in ["Phone", "Email", "SMS", "Facebook", "Snail Mail"]:
    cmeth = models.ContactMethod(name=contact_method)
    cmeth.save()

for cont_res in ["Communicated health information to patient", "Communicated health information to someone who translated for patient", "Spoke to individual who knows patient", "No answer, reached voicemail and left voicemail", "No answer, reached voicemail and didn't leave voicemail", "No answer, no voicemail option", "Phone number disconnected", "Email bounced back", "Busy signal", "Wrong number"]:
    print cont_res
    rslt = followup_models.ContactResult(name=cont_res)
    rslt.save()

for dx_type in ["Cardiovascular", "Dermatological", "Diabetes", "Gastrointestinal", "Infectious Disease (e.g. flu or HIV)", "Mental Health", "Musculoskeletal", "Neurological", "OB/GYN", "Physical Exam", "Respiratory", "Rx Refill", "Urogenital", "Vaccination", "Weight Concerns", "Other"]:
    d = models.DiagnosisType(name=dx_type)
    d.save()

f = models.ReferralLocation(name="SNHC")
f.save()

s = followup_models.NoAptReason(name="Problem resolved")
s.save()

s = followup_models.NoShowReason(name="Something came up")
s.save()

s = models.ReferralType(name="PCP")
s.save()

print "done!"
