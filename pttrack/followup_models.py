'''The datamodels for all various types required for followup tracking in  the
SNHC clintools patient tracking system'''
from django.db import models
from pttrack import models as mymodels
import django.utils.timezone

# pylint: disable=I0011,E1305


class ReferralType(models.Model):
    '''Simple text-contiaining class for storing the different kinds of
    clinics a patient can be referred to (e.g. PCP, ortho, etc.)'''

    name = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.name


class NoShowReason(models.Model):
    '''Simple text-contiaining class for storing the different reasons a
    patient might not have gone to a scheduled appointment.'''

    name = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.name

class NoAptReason(models.Model):
    '''Simple text-contiaining class for storing the different kinds of
    clinics a patient can be referred to (e.g. PCP, ortho, etc.)'''

    name = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.name


class ContactMethod(models.Model):
    '''Simple text-contiaining class for storing the method of contacting a
    patient for followup followed up with (i.e. phone, email, etc.)'''

    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name


class ContactResult(models.Model):
    '''Abstract base model for representing the resolution to a followup
    attempt with a patient (e.g. no answer w/ voicemail).'''

    name = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.name


class PCPLocation(models.Model):
    '''Data model for a PCP Location'''

    name = models.CharField(max_length=300)
    address = models.TextField()

    def __unicode__(self):
        return self.name


class Followup(mymodels.Note):
    '''The base followup class used in all different types of patient followup
    notes.'''

    class Meta:  # pylint: disable=W0232,R0903,C1001,C0111
        abstract = True

    written_datetime = models.DateTimeField(default=django.utils.timezone.now)

    contact_method = models.ForeignKey(ContactMethod)
    contact_resolution = models.ForeignKey(ContactResult)

    comments = models.TextField()

    def attribution(self):
        return " ".join([self.author.name(), "on", str(self.written_date())])

    def written_date(self):
        return self.written_datetime.date()

    def __unicode__(self):
        return " ".join(["Followup for ", self.patient.name(), " on ",
                         str(self.written_date())])


class VaccineFollowup(Followup):
    '''Datamodel for a followup of a vaccine administration'''

    SUBSQ_DOSE_HELP = "Are they coming back for another dose?"
    subsq_dose = models.BooleanField(help_text=SUBSQ_DOSE_HELP)

    DOSE_DATE_HELP = "When is the next dose?"
    dose_date = models.DateField(blank=True,
                                 null=True,
                                 help_text=DOSE_DATE_HELP)

    def type(self):
        return "Vaccine"

    def short_text(self):
        return ""


class LabFollowup(Followup):
    '''Datamodel for a follow up for lab results.'''

    CS_HELP = "Were you able to communicate the results?"
    communication_success = models.BooleanField(help_text=CS_HELP)

    def type(self):
        return "Labs"

    def short_text(self):
        return ("successfully reached" if self.communication_success else
                "failed to reach") + " patient regarding lab results."


class ReferralFollowup(Followup):
    '''Datamodel for a PCP referral followup.'''

    bREF_HELP = "Does the patient have an appointment?"
    has_appointment = models.BooleanField(help_text=bREF_HELP)

    APP_HELP = "Where is the appointment?"
    apt_location = models.ForeignKey(PCPLocation,
                                     blank=True,
                                     null=True,
                                     help_text=APP_HELP)

    PTSHOW_OPTS = [("Yes", "Yes"),
                   ("No", "No"),
                   ("Not yet", "Not yet")]

    PTSHOW_HELP = "Did the patient show up to the appointment?"
    pt_showed = models.CharField(help_text=PTSHOW_HELP,
                                 max_length=7,
                                 choices=PTSHOW_OPTS)

    REFTYPE_HELP = "What kind of provider was the patient referred to?"
    referral_type = models.ForeignKey(ReferralType, help_text=REFTYPE_HELP)

    NOAPT_HELP = "If the patient didn't make an appointment, why not?"
    noapt_reason = models.ForeignKey(NoAptReason,
                                     help_text=NOAPT_HELP,
                                     blank=True,
                                     null=True)

    NOSHOW_HELP = "If the patient didn't go to appointment, why not?"
    noshow_reason = models.ForeignKey(NoShowReason,
                                      help_text=NOSHOW_HELP,
                                      blank=True,
                                      null=True)

    def type(self):
        return "Referral"

    def short_text(self):
        return ""
