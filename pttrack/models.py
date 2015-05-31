from django.db import models
from django.core.exceptions import ValidationError
from django.forms import ModelForm
import django.utils.timezone
# Create your models here.


def validate_zip(value):
    '''verify that the given value is in the ZIP code format'''
    if len(str(value)) != 5:
        raise ValidationError('%s is not a valid ZIP, because it has %d digits.' %
                              value, len(value))

    if not str(value).isdigit():
        raise ValidationError("%s is not a valid ZIP, because it contains non-digit characters." %
                              value)


class Language(models.Model):
    language_name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.language_name


class Person(models.Model):

    class Meta:
        abstract = True

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=50)

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    GENDER_OPTS = ((MALE, "Male"),
                   (FEMALE, "Female"),
                   (OTHER, "Other"))
    gender = models.CharField(max_length=1,
                              choices=GENDER_OPTS)

    def name(self, reverse=True, middle_short=False):
        if self.middle_name:
            if middle_short:
                middle = self.middle_name[0]+"."
            else:
                middle = self.middle_name
        else:
            middle = ""

        if reverse:
            return " ".join([self.last_name+",",
                             self.first_name,
                             middle])
        else:
            return " ".join([self.first_name,
                             middle,
                             self.last_name])


class Patient(Person):
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50,
                            default="St. Louis")
    state = models.CharField(max_length=2,
                             default="MO")
    zip_code = models.CharField(max_length=5,
                                validators=[validate_zip])

    date_of_birth = models.DateField()
    language = models.ForeignKey(Language)

    #TODO: load ethnicity options from a file?
    ethnicity = models.CharField(max_length=50)

    lost = "LTFO"
    completed = "COMP"
    binned = "BIN"
    PCP_followup = "PCP"
    COMP_OPTS = ((lost, "Filed - Lost to follow up"),
                 (completed, "Filed - encounter completed"),
                 (binned, "In WashU Bin"),
                 (PCP_followup, "PCP Referral Follow-up"))

    comp_status = models.CharField(max_length=4,
                                   choices=COMP_OPTS)

    def age(self):
        import datetime
        return (datetime.date.today()-self.date_of_birth).days/365


class Provider(Person):

    ATTENDING = "ATTEND"
    CLINICAL = "CLIN"
    PRECLINICAL = "PRECLIN"
    TYPE = ((ATTENDING, "Attending Physician"),
            (CLINICAL, "Clinical Medical Student"),
            (PRECLINICAL, "Preclinical Medical Student"))
    provider_type = models.CharField(max_length=6,
                                     choices=TYPE)

    email = models.EmailField()

    def is_preclinical(self):
        return self.provider_type == self.PRECLINICAL

    def is_clinical(self):
        return self.provider_type == self.CLINICAL

    def is_attending(self):
        return self.provider_type == self.ATTENDING


class ClinicDate(models.Model):
    BASIC = "BASIC"
    PSYCH = "PSYCH"
    ORTHO = "ORTHO"
    DERM = "DERMA"

    CLINIC_TYPES = ((BASIC, '(Saturday) Basic Care Clinic'),
                    (PSYCH, 'Depression & Anxiety Specialty'),
                    (ORTHO, 'Muscle and Joint Pain Specialty'),
                    (DERM, 'Dermatology Specialty'))

    clinic_type = models.CharField(max_length=5,
                                   choices=CLINIC_TYPES,
                                   default=BASIC)

    #TODO: don't override "date" class with this variable
    date = models.DateField()
    gcal_id = models.CharField(max_length=50)

    def is_specialty(self):
        return not self.clinic_type is self.BASIC


class Note(models.Model):
    class Meta:
        abstract = True

    author = models.ForeignKey(Provider, blank=True)
    patient = models.ForeignKey(Patient)


class Workup(Note):
    clinic_day = models.ForeignKey(ClinicDate)

    CC = models.CharField(max_length=300)
    #TODO: CC categories (ICD10?)

    HPI = models.TextField()
    PMH = models.TextField()
    PSH = models.TextField()
    SocHx = models.TextField()
    FamHx = models.TextField()
    allergies = models.TextField()
    meds = models.TextField()

    diagnosis = models.CharField(max_length=100)
    #TODO: diagnosis categories (ICD10?)

    #TODO: process as separate model
    labs = models.TextField()

    plan = models.TextField()


class Followup(Note):
    note = models.TextField()

    written_date = models.DateTimeField(default=django.utils.timezone.now)
    next_action = models.DateField(blank=True)
