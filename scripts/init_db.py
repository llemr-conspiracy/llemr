'''
This script builds in the fundamental data required to use the webapp. If there
are no clinic types, for example, it becomes impossible to enter a workup,
because workups depend on clinic type ForeignKeys. This can be run to seed a
new database in production, or just as part of the reset_db.sh script used to
rebuild the database when debugging.
'''

from pttrack import models as core
from followup import models as followup
from workup import models as workup
from referral import models as referral

for lang_name in ["English", "Arabic", "Armenian", "Bengali", "Chinese",
                  "Croatian", "Czech", "Danish", "Dutch", "Finnish", "French",
                  "French Creole", "German", "Greek", "Hebrew", "Hindi/Urdu",
                  "Hungarian", "Italian", "Japanese", "Korean", "Lithuanian",
                  "Persian", "Polish", "Portuguese", "Romanian", "Russian",
                  "Samoan", "Serbocroatian", "Slovak", "Spanish", "Swedish",
                  "Tagalog", "Thai/Laotian", "Turkish", "Ukrainian",
                  "Vietnamese", "Yiddish"]:
    l = core.Language(name=lang_name)
    l.save()

for ethnic_name in ["White", "Native Hawaiian or Other Pacific Islander",
                    "Hispanic or Latino", "Black or African American",
                    "Asian", "American Indian or Alaska Native", "Other"]:
    e = core.Ethnicity(name=ethnic_name)
    e.save()

for lname in ["Male", "Female", "Other"]:
    g = core.Gender(long_name=lname, short_name=lname[0])
    g.save()

for (lname, can_sign, part_staff) in [("Attending Physician", True, False),
                          ("Preclinical Medical Student", False, False),
                          ("Clinical Medical Student", False, False),
                          ("Coordinator", False, True)]:
    p = core.ProviderType(long_name=lname, short_name=lname.split()[0],
                            signs_charts=can_sign, staff_view=part_staff)
    p.save()


for clintype in ["Basic Care Clinic", "Depression & Anxiety Clinic",
                 "Dermatology Clinic", "Muscle and Joint Pain Clinic"]:
    t = workup.ClinicType(name=clintype)
    t.save()

for ai_type in ["Vaccine Reminder", "Lab Follow-Up", "PCP Follow-Up", "Other"]:
    i = core.ActionInstruction(instruction=ai_type)
    i.save()

for contact_method in ["Phone", "Email", "Snail Mail"]:
    cmeth = core.ContactMethod(name=contact_method)
    cmeth.save()

followup.ContactResult.objects.create(
    name="Communicated health information to patient",
    attempt_again=False,
    patient_reached=True)
followup.ContactResult.objects.create(
    name="No answer, reached voicemail and didn't leave voicemail",
    attempt_again=True,
    patient_reached=False)
followup.ContactResult.objects.create(
    name="Phone number disconnected",
    attempt_again=False,
    patient_reached=False)

for dx_type in ["Cardiovascular", "Dermatological", "Endocrine", 
                "Eyes and ENT", "GI", "Infectious Disease (e.g. flu or HIV)", 
                "Mental Health", "Musculoskeletal", "Neurological", 
                "OB/GYN", "Physical Exam", "Respiratory", "Rx Refill", 
                "Urogenital", "Vaccination/PPD", "Other"]:
    d = workup.DiagnosisType(name=dx_type)
    d.save()

for referral_location in [
  "Back to SNHC", "SNHC Depression and Anxiety Specialty Night",
  "SNHC Dermatology Specialty Night", "SNHC OB/GYN Specialty Night",
  "Barnes Jewish Center for Outpatient Health (COH)",
  "BJC Behavioral Health (for Psych)",
  "St. Louis Dental Education and Oral Health Clinic",
  "St. Louis County Department of Health: South County Health Center",
  "Other"]:
    f = core.ReferralLocation(name=referral_location)
    f.save()

for noapt_reason in [
  "Not interested in further medical care at this time",
  "Too busy/forgot to contact provider",
  "Lost provider contact information",
  "Cannot reach provider",
  "Contacted provider but did not successfully schedule appointment",
  "Appointment wait time is too long",
  "No transportation to get to appointment",
  "Appointment times do not work with patient's schedule",
  "Cannot afford appointment", "Other"]:
    s = followup.NoAptReason(name=noapt_reason)
    s.save()

for noshow_reason in [
  "Schedule changed in conflict with appointment",
  "Didn't have transportation to appointment",
  "Worried about cost of appointment",
  "Too sick to go to appointment",
  "Felt better and decided didn't need appointment",
  "Someone counseled patient against appointment",
  "Forgot about appointment"]:
    s = followup.NoShowReason(name=noshow_reason)
    s.save()

for refer_type in ["PCP: chronic condition management",
                   "PCP: gateway to specialty care",
                   "PCP: preventative care (following well check up)",
                   "PCP: other acute conditions", "Specialty care", "Other"]:
    s = core.ReferralType(name=refer_type)
    s.save()

for (location, is_fqhc, is_specialty) in [("Affina", True, False),
             ("Family Care Center", True, False),
             ("COH", False, True)]:
    r = referral.ReferralLocation(name=location, is_fqhc=is_fqhc, is_specialty=is_specialty)
    r.save()

core.DocumentType.objects.create(name="Silly picture")

print "done!"
