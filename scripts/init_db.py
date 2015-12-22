'''
This script builds in the fundamental data required to use the webapp. If there
are no clinic types, for example, it becomes impossible to enter a workup,
because workups depend on clinic type ForeignKeys. This can be run to seed a
new database in production, or just as part of the reset_db.sh script used to
rebuild the database when debugging.
'''

from pttrack import models as core
from followup import models as followup
from datetime import date

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

for ethnic_name in ["Afghanistani", "African American", "Albanian", "Algerian",
                    "Andorran", "Angolan", "Argentinian", "Armenian",
                    "Australian", "Bolivian", "Bosnian", "Brazilian",
                    "Canadian", "Caucasian", "Chilean", "Chinese", "Colombian",
                    "Croatian", "Czechoslovakian", "Egyptian", "French",
                    "German", "Greek", "Haitian", "Hispanic", "Honduran",
                    "Indian", "Indonesian", "Iranian", "Iraqi", "Irish",
                    "Israeli", "Italian," "Jamaican", "Japanese", "Jordanian",
                    "Kenyan", "Korean", "Laotian", "Latvian", "Lebanese",
                    "Libyan", "Malaysian", "Mexican", "Namibian", "Norwegian",
                    "Pakistani", "Romanian", "Russian", "Rwandan", "Samoan",
                    "Serbian," "Somalian", "South African", "Spanish"
                    "Syrian", "Taiwanese", "Turkish", "Vietnamese", "Yemenese",
                    "Zimbabwean"]:
    e = core.Ethnicity(name=ethnic_name)
    e.save()

for lname in ["Male", "Female", "Other"]:
    g = core.Gender(long_name=lname, short_name=lname[0])
    g.save()

core.Patient.objects.create(
    first_name="Juggie",
    last_name="Brodeltein",
    middle_name="Bayer",
    phone='+49 178 236 5288',
    gender=g,
    address='Schulstrasse 9',
    city='Munich',
    state='BA',
    zip_code='63108',
    pcp_preferred_zip='63018',
    date_of_birth=date(1990, 01, 01))

for (lname, can_sign) in [("Attending Physician", True),
                          ("Preclinical Medical Student", False),
                          ("Clinical Medical Student", False),
                          ("Coordinator", False)]:
    p = core.ProviderType(long_name=lname, short_name=lname.split()[0],
                          signs_charts=can_sign)
    p.save()


for clintype in ["Basic Care Clinic", "Depression & Anxiety Clinic",
                 "Dermatology Clinic", "Muscle and Joint Pain Clinic"]:
    t = core.ClinicType(name=clintype)
    t.save()

for ai_type in ["Vaccine Reminder", "Lab Follow-Up", "PCP Follow-Up", "Other"]:
    i = core.ActionInstruction(instruction=ai_type)
    i.save()

for contact_method in ["Phone", "Email", "SMS", "Facebook", "Snail Mail"]:
    cmeth = core.ContactMethod(name=contact_method)
    cmeth.save()

for cont_res in [
  "Communicated health information to patient",
  "Communicated health information to someone who translated for patient",
  "Spoke to individual who knows patient",
  "No answer, reached voicemail and left voicemail",
  "No answer, reached voicemail and didn't leave voicemail",
  "No answer, no voicemail option", "Phone number disconnected",
  "Email bounced back", "Busy signal", "Wrong number"]:
    print cont_res
    rslt = followup.ContactResult(name=cont_res)
    rslt.save()

for dx_type in ["Cardiovascular", "Dermatological", "Endocrine", 
                "Eyes and ENT", "GI", "Infectious Disease (e.g. flu or HIV)", 
                "Mental Health", "Musculoskeletal", "Neurological", 
                "OB/GYN", "Physical Exam", "Respiratory", "Rx Refill", 
                "Urogenital", "Vaccination/PPD", "Other"]:
    d = core.DiagnosisType(name=dx_type)
    d.save()

for referral_location in [
  "Back to SNHC", "SNHC Depression and Anxiety Specialty Night",
  "SNHC Dermatology Specialty Night", "SNHC OB/GYN Specialty Night",
  "Barnes Jewish Center for Outpatient Health (COH)",
  "BJC Behavioral Health (for Psych)",
  "St. Louis Dental Education and Oral Health Clinic",
  "Betty Jean Kerr Peoples Health Centers: Central",
  "Betty Jean Kerr Peoples Health Centers: North",
  "Betty Jean Kerr Peoples Health Centers: West",
  "Crider Health Center: Union", "Crider Health Center: Warrenton",
  "Crider Health Center: Wentzville", "Family Care Health Centers: Carondelet",
  "Family Care Health Centers: Forest Park Southeast",
  "Affinia Healthcare (formerly Grace Hill)",
  "Myrtle Hilliard Davis: Comprehensive",
  "Myrtle Hilliard Davis: Florence Hill",
  "Myrtle Hilliard Davis: Homer G. Phillips",
  "St. Louis County Department of Health: John C. Murphy Health Center",
  "St. Louis County Department of Health: " +
  "North Central Community Health Center",
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

core.DocumentType.objects.create(name="Silly picture")

print "done!"
