from pttrack import models
from pttrack import followup_models
from datetime import date

for lang_name in ["English", "Arabic", "Armenian", "Bengali", "Chinese",
                  "Croatian", "Czech", "Danish", "Dutch", "Finnish", "French",
                  "French Creole", "German", "Greek", "Hebrew", "Hindi/Urdu",
                  "Hungarian", "Italian", "Japanese", "Korean", "Lithuanian",
                  "Persian", "Polish", "Portuguese", "Romanian", "Russian",
                  "Samoan", "Serbocroatian", "Slovak", "Spanish", "Swedish",
                  "Tagalog", "Thai/Laotian", "Turkish", "Ukrainian",
                  "Vietnamese", "Yiddish"]:
    l = models.Language(name=lang_name)
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
    e = models.Ethnicity(name=ethnic_name)
    e.save()

for lname in ["Male", "Female", "Other"]:
    g = models.Gender(long_name=lname, short_name=lname[0])
    g.save()

for (lname, can_sign) in [("Attending Physician", True),
                          ("Preclinical Medical Student", False),
                          ("Clinical Medical Student", False),
                          ("Coordinator", False)]:
    p = models.ProviderType(long_name=lname, short_name=lname.split()[0],
                            signs_charts=can_sign)
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

for cont_res in [
  "Communicated health information to patient",
  "Communicated health information to someone who translated for patient",
  "Spoke to individual who knows patient",
  "No answer, reached voicemail and left voicemail",
  "No answer, reached voicemail and didn't leave voicemail",
  "No answer, no voicemail option", "Phone number disconnected",
  "Email bounced back", "Busy signal", "Wrong number"]:
    print cont_res
    rslt = followup_models.ContactResult(name=cont_res)
    rslt.save()

for dx_type in ["Cardiovascular", "Dermatological", "Endocrine", 
                "Eyes and ENT", "GI", "Infectious Disease (e.g. flu or HIV)", 
                "Mental Health", "Musculoskeletal", "Neurological", 
                "OB/GYN", "Physical Exam", "Respiratory", "Rx Refill", 
                "Urogenital", "Vaccination/PPD", "Other"]:
    d = models.DiagnosisType(name=dx_type)
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
    f = models.ReferralLocation(name=referral_location)
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
    s = followup_models.NoAptReason(name=noapt_reason)
    s.save()

for noshow_reason in [
  "Schedule changed in conflict with appointment",
  "Didn't have transportation to appointment",
  "Worried about cost of appointment",
  "Too sick to go to appointment",
  "Felt better and decided didn't need appointment",
  "Someone counseled patient against appointment",
  "Forgot about appointment"]:
    s = followup_models.NoShowReason(name=noshow_reason)
    s.save()

for refer_type in ["PCP: chronic condition management",
                   "PCP: gateway to specialty care",
                   "PCP: preventative care (following well check up)",
                   "PCP: other acute conditions", "Specialty care", "Other"]:
    s = models.ReferralType(name=refer_type)
    s.save()

print "done!"
