'''
This script builds in the fundamental data required to use the webapp. If there
are no clinic types, for example, it becomes impossible to enter a workup,
because workups depend on clinic type ForeignKeys. This can be run to seed a
new database in production, or just as part of the reset_db.sh script used to
rebuild the database when debugging.
'''
from __future__ import print_function
from __future__ import unicode_literals

from osler.core import models as core
from followup import models as followup
from osler.workup import models as workup
from referral import models as referral

for lang_name in [ "Deutsch", "Englisch", "Arabisch", "Bengalisch", "Chinesisch",
                  "Kroatisch", "Tschechisch", "Dänisch", "Niederländisch", "Finnisch", "Französisch",
                   "Griechisch", "Hebräisch", "Hindi/Urdu",
                  "Ungarisch", "Italienisch", "Litauisch",
                  "Persisch", "Polnisch", "Portugisisch", "Rumänisch", "Russisch",
                   "Slovakisch", "Spanisch", "Schwedisch",
                 "Türkisch", "Ukrainisch", "Andere"
                 ]:
    l = core.Language(name=lang_name)
    l.save()

for ethnic_name in ["Weiß",
                    "Schwarz oder Afroamerikanisch",
                    "Asiatisch", "Indisch", "Andere"]:
    e = core.Ethnicity(name=ethnic_name)
    e.save()

for lname in ["Männlich", "Weiblich", "Divers"]:
    g = core.Gender(long_name=lname, short_name=lname[0])
    g.save()

for (lname, can_sign, part_staff) in [("Arzt", True, False),
                          ("Junior", False, False),
                          ("Senior", False, False),
                          ("Koordinator", False, True)]:
    p = core.ProviderType(long_name=lname, short_name=lname.split()[0],
                            signs_charts=can_sign, staff_view=part_staff)
    p.save()


for clintype in ["Normale Klinik", "Depressionen und Angst",
                 "Dermatologisch", "Orthopädisch"]:
    t = workup.ClinicType(name=clintype)
    t.save()

for ai_type in ["Impfungs-Erinnerung", "Labor Nachebsprechung", "PCP Nachbesprechung", "Andere"]:
    i = core.ActionInstruction(instruction=ai_type)
    i.save()

for contact_method in ["Telefon", "Email", "Andere"]:
    cmeth = core.ContactMethod(name=contact_method)
    cmeth.save()

followup.ContactResult.objects.create(
    name="Medizinische Infos wurden mit Patienten abgeklärt",
    attempt_again=False,
    patient_reached=True)
followup.ContactResult.objects.create(
    name="Keine Antwort, Patient wurde angerufen, hat aber nicht abgenommen",
    attempt_again=True,
    patient_reached=False)
followup.ContactResult.objects.create(
    name="Telefonnummer existiert nicht",
    attempt_again=False,
    patient_reached=False)

for dx_type in ["Kardiovaskulär", "Dermatologisch", "Endokrinologisch",
                "Auge und Hals-Nasen-Ohren", "Gastrointestinal", "Infektiös",
                "Mentale Erkrankungen", "Orthopädisch", "Neurologisch",
                "Gynäkologisch", "Körperliche Untersuchung", "Respiratorisch", "Rezeptor-Auffrischung",
                "Urogenital", "Impfung", "Andere"]:
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

# for noshow_reason in [
#   "Schedule changed in conflict with appointment",
#   "Didn't have transportation to appointment",
#   "Worried about cost of appointment",
#   "Too sick to go to appointment",
#   "Felt better and decided didn't need appointment",
#   "Someone counseled patient against appointment",
#   "Forgot about appointment"]:
#     s = followup.NoShowReason(name=noshow_reason)
#     s.save()

for refer_type, is_fqhc in [("PCP", True),
                            ("Specialty care", False)]:
    s = core.ReferralType(name=refer_type, is_fqhc=is_fqhc)
    s.save()

spc_referral = core.ReferralType.objects.filter(is_fqhc=False).first()
pcp_referral = core.ReferralType.objects.filter(is_fqhc=True).first()
for (location, reftype) in [("Affina", pcp_referral),
                            ("Family Care Center", spc_referral),
                            ("COH", spc_referral)]:
    r = referral.ReferralLocation(name=location)
    r.save()
    # we do this so we don't get an M2M error
    r.care_availiable = refer_type
    r.save()

core.DocumentType.objects.create(name="Silly picture")

print("done!")
