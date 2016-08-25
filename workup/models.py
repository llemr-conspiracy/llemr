from django.db import models
from django.utils.timezone import now

from simple_history.models import HistoricalRecords
from django.core.urlresolvers import reverse

from pttrack.models import Note, Provider, ReferralLocation, ReferralType
from pttrack.validators import validate_attending

from .validators import validate_bp, validate_hr, validate_rr, validate_t, validate_height, validate_weight


class DiagnosisType(models.Model):
    '''Simple text-contiaining class for storing the different kinds of
    diagnosis a pateint can recieve.'''

    name = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.name


class ClinicType(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class ClinicDate(models.Model):
    clinic_type = models.ForeignKey(ClinicType)

    clinic_date = models.DateField()
    gcal_id = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.clinic_type)+" ("+str(self.clinic_date)+")"


class Workup(Note):
    '''Datamodel of a workup. Has fields specific to each part of an exam,
    along with SNHC-specific info about where the patient has been referred for
    continuity care.'''

    clinic_day = models.ForeignKey(ClinicDate)

    chief_complaint = models.CharField(max_length=1000,
                                       verbose_name="CC")
    diagnosis = models.CharField(max_length=1000,
                                 verbose_name="Dx")
    diagnosis_categories = models.ManyToManyField(DiagnosisType)

    HPI = models.TextField(verbose_name="HPI")
    PMH_PSH = models.TextField(verbose_name="PMH/PSH")
    meds = models.TextField(verbose_name="Medications")
    allergies = models.TextField()
    fam_hx = models.TextField(verbose_name="Family History")
    soc_hx = models.TextField(verbose_name="Social History")
    ros = models.TextField(verbose_name="ROS")

    hr = models.CharField(blank=True, null=True, max_length=12, validators=[validate_hr])
    bp = models.CharField(blank=True, null=True, max_length=12, validators=[validate_bp])

    rr = models.CharField(blank=True, null=True, max_length=12, validators=[validate_rr])
    t = models.CharField(blank=True, null=True, max_length=12, validators=[validate_t])

    # this is a hotfix that needs to be changed in terms of error handeling for the entire form so that 
    # people are not confused when they cannot submit their form.
    height = models.CharField(blank=True, null=True, max_length=12, validators=[validate_height])
    weight = models.CharField(blank=True, null=True, max_length=12, validators=[validate_weight])

    pe = models.TextField(verbose_name="Physical Examination")

    labs_ordered_quest = models.TextField(
        blank=True, null=True, verbose_name="Labs Ordered from Quest")
    labs_ordered_internal = models.TextField(
        blank=True, null=True, verbose_name="Labs Ordered Internally")

    rx = models.TextField(blank=True, null=True,
                          verbose_name="Prescription Orders")

    got_voucher = models.BooleanField(default=False)
    voucher_amount = models.PositiveSmallIntegerField(blank=True, null=True)
    patient_pays = models.PositiveSmallIntegerField(blank=True, null=True)

    got_imaging_voucher = models.BooleanField(default=False)
    imaging_voucher_amount = models.PositiveSmallIntegerField(blank=True, null=True)
    patient_pays_imaging = models.PositiveSmallIntegerField(blank=True, null=True)

    referral_type = models.ManyToManyField(ReferralType, blank=True)
    referral_location = models.ManyToManyField(ReferralLocation, blank=True)

    will_return = models.BooleanField(default=False,
                                      help_text="Will the pt. return to SNHC?")

    A_and_P = models.TextField()

    signer = models.ForeignKey(Provider,
                               blank=True, null=True,
                               related_name="signed_workups",
                               validators=[validate_attending])
    signed_date = models.DateTimeField(blank=True, null=True)

    history = HistoricalRecords()

    def sign(self, user, active_role=None):
        '''
        Signs this workup. The active_role parameter isn't necessary if the
        user has only one role.
        '''

        if active_role is None:
            if len(user.provider.clinical_roles.all()) != 1:
                raise ValueError("For users with > role, it must be provided.")
            else:
                active_role = user.provider.clinical_roles.all()[0]
        elif active_role not in user.provider.clinical_roles.all():
            raise ValueError(
                "Provider {p} doesn't have role {r}!".format(
                    p=user.provider, r=active_role))

        if active_role.signs_charts:
            assert active_role in user.provider.clinical_roles.all()

            self.signed_date = now()
            self.signer = user.provider
        else:
            raise ValueError("You must be an attending to sign workups.")

    def signed(self):
        '''Has this workup been attested? Returns True if yes, False if no.'''
        return self.signer is not None

    def short_text(self):
        '''
        Return the 'short text' representation of this Note. In this case, it's
        simply the CC
        '''
        return self.chief_complaint

    # TODO: this is not consistent with the written datetime that we see for
    # the rest of the Note subclasses.
    def written_date(self):
        '''
        Returns the date (not datetime) this workup was written on.
        '''
        return self.clinic_day.clinic_date

    def attribution(self):
        '''Builds an attribution string of the form Doe, John on DATE'''
        return " ".join([str(self.author), "on", str(self.written_date())])

    def url(self):
        return reverse('workup', args=(self.pk,))

    def __unicode__(self):
        return self.patient.name()+" on "+str(self.clinic_day.clinic_date)
