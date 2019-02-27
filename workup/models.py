from django.db import models
from django.utils.timezone import now

from simple_history.models import HistoricalRecords
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator

from pttrack.models import Note, Provider, ReferralLocation, ReferralType

from pttrack.validators import validate_attending
from . import validators as workup_validators


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

    class Meta:
        ordering = ["-clinic_date"]

    clinic_type = models.ForeignKey(ClinicType)

    clinic_date = models.DateField()
    gcal_id = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.clinic_type)+" ("+str(self.clinic_date)+")"


class ProgressNote(Note):
    title = models.CharField(max_length=200)
    text = models.TextField()

    history = HistoricalRecords()

    def short_text(self):
        return self.title


class Workup(Note):
    '''Datamodel of a workup. Has fields specific to each part of an exam,
    along with SNHC-specific info about where the patient has been referred for
    continuity care.'''

    attending = models.ForeignKey(
        Provider, null=True, blank=True, related_name="attending_physician",
        validators=[validate_attending],
        help_text="Which attending saw the patient?")
    other_volunteer = models.ManyToManyField(
        Provider, blank=True, related_name="other_volunteer",
        help_text="Which other volunteer(s) did you work with (if any)?")

    clinic_day = models.ForeignKey(ClinicDate, help_text="When was the patient seen?")

    chief_complaint = models.CharField(max_length=1000, verbose_name="CC")
    diagnosis = models.CharField(max_length=1000, verbose_name="Dx")
    diagnosis_categories = models.ManyToManyField(DiagnosisType)

    HPI = models.TextField(verbose_name="HPI")
    PMH_PSH = models.TextField(verbose_name="PMH/PSH")
    meds = models.TextField(verbose_name="Medications")
    allergies = models.TextField()
    fam_hx = models.TextField(verbose_name="Family History")
    soc_hx = models.TextField(verbose_name="Social History")
    ros = models.TextField(verbose_name="ROS")

    # represented internally in per min
    hr = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Heart Rate")

    # represented internally as mmHg
    bp_sys = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Systolic",
        validators=[workup_validators.validate_bp_systolic])
    bp_dia = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Diastolic",
        validators=[workup_validators.validate_bp_diastolic])

    # represented internally in per min
    rr = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Respiratory Rate")

    # represented internally in Fahrenheit
    t = models.DecimalField(
        max_digits=4, decimal_places=1,
        blank=True, null=True,
        verbose_name="Temperature")

    # represented internally as inches
    height = models.PositiveSmallIntegerField(
        blank=True, null=True)
    # represented internally as kg
    weight = models.DecimalField(
        max_digits=5, decimal_places=1,
        blank=True, null=True)

    pe = models.TextField(verbose_name="Physical Examination")

    labs_ordered_quest = models.TextField(
        blank=True, null=True, verbose_name="Labs Ordered from Quest")
    labs_ordered_internal = models.TextField(
        blank=True, null=True, verbose_name="Labs Ordered Internally")

    rx = models.TextField(blank=True, null=True,
                          verbose_name="Prescription Orders")

    got_voucher = models.BooleanField(default=False)
    voucher_amount = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)])
    patient_pays = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)])

    got_imaging_voucher = models.BooleanField(default=False)
    imaging_voucher_amount = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)])
    patient_pays_imaging = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)])

    # Please note that these are no longer shown on the form and will not
    # be filled out because the referral app handles this functionality
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
        """Signs this workup.

        The active_role parameter isn't necessary if the user has only one role.
        """

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
