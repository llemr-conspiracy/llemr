from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.conf import settings

from osler.core.models import Note, ReferralLocation, ReferralType, Encounter
from osler.workup import validators as workup_validators

from osler.users.utils import group_has_perm

from simple_history.models import HistoricalRecords

from django.utils.translation import gettext_lazy as _


class DiagnosisType(models.Model):
    '''Simple text-contiaining class for storing the different kinds of
    diagnosis a pateint can recieve.'''

    class Meta(object):
        ordering = ["name"]

    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class AttestationMixin(models.Model):

    signer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.PROTECT,
        related_name="signed_%(app_label)s_%(class)s")
    signed_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def sign(self, user, group):
        """Signs this workup."""
        user_has_group = user.groups.filter(pk=group.pk).exists()
        if user_has_group and self.group_can_sign(group):
            self.signed_date = now()
            self.signer = user
        else:
            raise ValueError("Special permissions are required to sign notes.")

    def signed(self):
        """Has this workup been attested? Returns True if yes, False if no."""
        return self.signer is not None

    def attribution(self):
        """Builds an attribution string of the form Doe, John on DATE"""
        return " ".join([str(self.author), "on", str(self.written_date())])

    @classmethod
    def get_sign_perm(cls):
        """returns name of signing perm"""
        return 'workup.sign_%s' % cls.__name__

    @classmethod
    def group_can_sign(cls, group):
        """takes a group and checks if it has sign permission to this object."""
        return group_has_perm(group, cls.get_sign_perm())


class AbstractBasicNote(Note):

    title = models.CharField(max_length=200)
    text = models.TextField()
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        u = '{} on at {} by {}'.format(
            self.title,
            self.written_datetime.strftime('%c'),
            self.author)
        return u

    def short_text(self):
        return self.title


class BasicNote(AbstractBasicNote):

    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('basic-note-detail', args=[str(self.id)])


class AttestableBasicNote(AbstractBasicNote, AttestationMixin):

    class Meta:
        permissions = [
            ('sign_AttestableBasicNote', "Can sign note")
            ]

    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('attestable-basic-note-detail', args=[str(self.id)])


class Workup(Note, AttestationMixin):
    """Model for a medical student H&P for an outpatient clinic setting.

    Has fields specific to each part of an exam, along with SNHC-specific
    info about where the patient has been referred for continuity care.
    """

    class Meta:
        permissions = [
            ('export_pdf_Workup', 'Can export note PDF'),
            ('sign_Workup', "Can sign note")
            ]
        ordering = ['-encounter__clinic_day']

    attending = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        related_name="attending_physician",
        on_delete=models.PROTECT,
        help_text="Which attending saw the patient?")

    other_volunteer = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="other_volunteer",
        help_text="Which other volunteer(s) did you work with (if any)?")

    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE)

    chief_complaint = models.CharField(max_length=1000, verbose_name="CC", blank=True)
    diagnosis = models.CharField(max_length=1000, verbose_name="Dx", blank=True, null=True)
    diagnosis_categories = models.ManyToManyField(DiagnosisType, verbose_name="Diagnosis Categories", blank=True)

    hpi = models.TextField(verbose_name="HPI", blank=True)
    pmh = models.TextField(verbose_name="PMH", blank=True)
    psh = models.TextField(verbose_name="PSH", blank=True)
    meds = models.TextField(verbose_name="Medications", blank=True)
    allergies = models.TextField(blank=True)
    fam_hx = models.TextField(verbose_name="Family History", blank=True)
    soc_hx = models.TextField(verbose_name="Social History", blank=True)
    ros = models.TextField(verbose_name="ROS", blank=True)

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

    pe = models.TextField(verbose_name="Physical Examination", blank=True)

    labs_ordered_external = models.TextField(
        blank=True, null=True, verbose_name="Labs Ordered Externally")
    labs_ordered_internal = models.TextField(
        blank=True, null=True, verbose_name="Labs Ordered Internally")

    rx = models.TextField(
        blank=True, verbose_name="Prescription Orders",
        help_text=_("Ex: Ibuprofen 200mg 1 tab PO PRN Q8H for pain #28"))

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

    a_and_p = models.TextField(verbose_name="A and P", blank=True)

    is_pending = models.BooleanField(default=False)

    history = HistoricalRecords()

    def short_text(self):
        '''
        Return the 'short text' representation of this Note. In this case, it's
        simply the CC
        '''
        return self.chief_complaint

    def written_date(self):
        '''
        Returns the date (not datetime) this workup was written on.
        '''
        return self.encounter.clinic_day

    def get_absolute_url(self):
        return reverse('workup', args=[str(self.id)])

    def detail_url(self):
        return self.get_absolute_url()

    def __str__(self):
        return " ".join(
            (self.patient.name(), "on",
             self.encounter.clinic_day.strftime('%A, %B %d, %Y'))
        )

    def sign(self, user, group):
        if not self.is_pending:
            super().sign(user, group)
        else:
            raise ValueError("Pending workups cannot be signed.")


class Addendum(Note):
    '''Additional info to be associated with a workup'''

    text = models.TextField()
    workup = models.ForeignKey(Workup, verbose_name=_("Workup"), on_delete=models.CASCADE)
