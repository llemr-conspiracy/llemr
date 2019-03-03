'''The datamodels for the Osler core'''
from itertools import chain

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import now
from django.utils.text import slugify
import os
from django.core.urlresolvers import reverse

from simple_history.models import HistoricalRecords

from . import validators

# pylint: disable=I0011,missing-docstring,E1305

def make_filepath(instance, filename):
    '''
        Produces a unique file path for the upload_to of a FileField. This is
        important because any URL is 1) transmitted unencrypted and 2)
        automatically referred to any libraries we include (i.e. Bootstrap,
        AngularJS).

        The produced path is of the form:
        "[model name]/[field name]/[random name].[filename extension]".

        Copypasta from https://djangosnippets.org/snippets/2819/
    '''


    field_name = 'image'
    carry_on = True
    while carry_on:
        new_filename = "%s.%s" % (User.objects.make_random_password(48),
                                  filename.split('.')[-1])
        #path = '/'.join([instance.__class__.__name__.lower(),field_name, new_filename])

        path = new_filename

        # if the file already exists, try again to generate a new filename
        carry_on = os.path.isfile(os.path.join(settings.MEDIA_ROOT, path))

    return path


class ContactMethod(models.Model):
    '''Simple text-contiaining class for storing the method of contacting a
    patient for followup followed up with (i.e. phone, email, etc.)'''

    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name


class ReferralType(models.Model):
    """The different kind of care availiable at a referral center."""

    name = models.CharField(max_length=100, primary_key=True)
    is_fqhc = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def slugify(self):
        return slugify(self.name)


class ReferralLocation(models.Model):
    """Location that we can refer to."""

    name = models.CharField(max_length=300)
    address = models.TextField()
    care_availiable = models.ManyToManyField(ReferralType)

    def __unicode__(self):
        if self.address:
            return self.name + " (" + self.address.splitlines()[0] + ")"
        else:
            return self.name


class Language(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name


class Ethnicity(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name


class ActionInstruction(models.Model):
    instruction = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.instruction


class ProviderType(models.Model):
    long_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30, primary_key=True)
    signs_charts = models.BooleanField(default=False)
    staff_view = models.BooleanField(default=False)

    def __unicode__(self):
        return self.short_name


class Gender(models.Model):
    long_name = models.CharField(max_length=30, primary_key=True)
    short_name = models.CharField(max_length=1)

    def __unicode__(self):
        return self.long_name

class Outcome(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class Person(models.Model):

    class Meta:
        abstract = True

    first_name = models.CharField(
        max_length=100, validators=[validators.validate_name])
    last_name = models.CharField(
        max_length=100, validators=[validators.validate_name])
    middle_name = models.CharField(
        max_length=100, blank=True, validators=[validators.validate_name])

    phone = models.CharField(max_length=40, null=True, blank=True)
    languages = models.ManyToManyField(Language, help_text="Specify here languages that are spoken at a level sufficient to be used for medical communication.")

    gender = models.ForeignKey(Gender)

    def name(self, reverse=True, middle_short=True):
        if self.middle_name:
            if middle_short:
                middle = "".join([mname[0]+"." for mname
                                  in self.middle_name.split()])
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


class Provider(Person):

    associated_user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                           blank=True, null=True)

    clinical_roles = models.ManyToManyField(ProviderType)

    needs_updating = models.BooleanField(default=False)

    history = HistoricalRecords()

    @property
    def username(self):
        return self.associated_user.username

    def __unicode__(self):
        return self.name()


class Patient(Person):

    case_managers = models.ManyToManyField(Provider)

    outcome = models.ForeignKey(Outcome, null=True, blank=True)

    address = models.CharField(max_length=200)

    city = models.CharField(max_length=50,
                            default="St. Louis")
    state = models.CharField(max_length=2,
                             default="MO")
    zip_code = models.CharField(max_length=5,
                                validators=[validators.validate_zip])
    country = models.CharField(max_length=100,
                               default="USA")


    pcp_preferred_zip = models.CharField(max_length=5,
                                         validators=[validators.validate_zip],
                                         blank=True,
                                         null=True)

    date_of_birth = models.DateField(help_text='MM/DD/YYYY',
        validators=[validators.validate_birth_date])

    patient_comfortable_with_english = models.BooleanField(default=True)

    ethnicities = models.ManyToManyField(Ethnicity)

    # Alternative phone numbers have up to 4 fields and each one is associated
    # with the person that owns phone

    # TODO: we should really come up with a better way of representing these
    # data

    alternate_phone_1_owner = models.CharField(max_length=40, blank=True, null=True)
    alternate_phone_1 = models.CharField(max_length=40, blank=True, null=True)

    alternate_phone_2_owner = models.CharField(max_length=40, blank=True, null=True)
    alternate_phone_2 = models.CharField(max_length=40, blank=True, null=True)

    alternate_phone_3_owner = models.CharField(max_length=40, blank=True, null=True)
    alternate_phone_3 = models.CharField(max_length=40, blank=True, null=True)

    alternate_phone_4_owner = models.CharField(max_length=40, blank=True, null=True)
    alternate_phone_4 = models.CharField(max_length=40, blank=True, null=True)

    preferred_contact_method = models.ForeignKey(ContactMethod, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)

    # If the patient is in clinic and needs a workup, that is specified by
    # needs_workup. Default value is false for all the previous patients

    needs_workup = models.BooleanField(default=True)

    history = HistoricalRecords()

    def age(self):
        return (now().date()-self.date_of_birth).days//365

    def __unicode__(self):
        return self.name()

    def active_action_items(self):
        '''return a list of ActionItems that are 1) not done and
        2) due today or before. The list is sorted by due_date'''

        return sorted(
            ActionItem.objects.filter(patient=self.pk)\
                .filter(completion_author=None)\
                .filter(due_date__lte=now().date()),
            key=lambda(ai): ai.due_date)

    def done_action_items(self):
        '''return the set of action items that are done, sorted
        by completion date'''

        return sorted(
            ActionItem.objects.filter(patient=self.pk)\
                .exclude(completion_author=None),
            key=lambda(ai): ai.completion_date)

    def inactive_action_items(self):
        '''return a list of action items that aren't done, but aren't
        due yet either, sorted by due date.'''

        return sorted(
            ActionItem.objects.filter(patient=self.pk)\
                .filter(completion_author=None)\
                .filter(due_date__gt=now().date()),
            key=lambda(ai): ai.due_date)

    def status(self):
        # The active_action_items, done_action_items, and inactive_action_items
        # aren't a big deal to use when getting just one patient
        # For the all_patients page though (one of the pages that use status),
        # hitting the db three times per patient adds up.
        # Here, we only hit the db once by asking the db for all action items
        # for a patient, then sorting them in memory.

        # Combine action items with referral followup requests for status
        patient_action_items = self.actionitem_set.all()
        referral_followup_requests = self.followuprequest_set.all()
        patient_action_items = list(chain(patient_action_items,
                                          referral_followup_requests))

        done = [ai for ai in patient_action_items if ai.completion_author is not None]
        overdue = [ai for ai in patient_action_items if ai.completion_author is None and ai.due_date <= now().date()]
        pending = [ai for ai in patient_action_items if ai.completion_author is None and ai.due_date > now().date()]

        if len(overdue) > 0:
            due_dates = ", ".join([str((now().date()-ai.due_date).days) for ai in overdue])
            return "Action items " + due_dates + " days past due"
        elif len(pending) > 0:
            next_item = min(pending, key=lambda k: k.due_date)
            tdelta = next_item.due_date - now().date()
            return "next action in "+str(tdelta.days)+" days"
        elif len(done) > 0:
            return "all actions complete"
        else:
            return "no pending actions"

    def followup_set(self):
        followups = []
        followups.extend(self.labfollowup_set.all())
        followups.extend(self.vaccinefollowup_set.all())
        followups.extend(self.referralfollowup_set.all())
        followups.extend(self.generalfollowup_set.all())

        return followups

    def latest_workup(self):
        """
        Keeping this method because it is used by WorkupCreate.get_initial in
            workup/views
        However, this is not used in all_patients in pttrack/views, because it
            gets all patients in prefetch_related instead of requesting for
            latest_workup individually.
        """
        wu_set = self.workup_set
        return wu_set.order_by("clinic_day__clinic_date").first()

    def notes(self):
        '''Returns a list of all the notes (workups and followups) associated
        with this patient ordered by date written.'''
        note_list = []

        note_list.extend(self.workup_set.all())
        note_list.extend(self.followup_set())
        note_list.extend(self.document_set.all())

        return sorted(note_list, key=lambda(k): k.written_datetime)

    def all_phones(self):
        '''Returns a list of tuples of the form (phone, owner) of all the
        phones associated with this patient.'''

        phones = [(self.phone, '')]
        phones.extend([(getattr(self, 'alternate_phone_'+str(i)),
                        getattr(self, 'alternate_phone_'+str(i)+'_owner'))
                       for i in range(1, 5)])

        return phones

    def toggle_active_status(self):
        ''' Will Activate or Inactivate the Patient'''
        self.needs_workup = not self.needs_workup

    def detail_url(self):
        return reverse('patient-detail', args=(self.pk,))

    def update_url(self):
        return reverse('patient-update', args=(self.pk,))

    def activate_url(self):
        return reverse('patient-activate-home', args=(self.pk,))


def require_providers_update():
    '''
    Sets needs_update to True for all providers
    Not sure where this should go
    Is an independent function that sets all providers so the setter doesn't
    have to figure out what to type.
    '''
    for provider in Provider.objects.all():
        provider.needs_updating = True
        provider.save()


class Note(models.Model):
    class Meta:
        abstract = True

    author = models.ForeignKey(Provider)
    author_type = models.ForeignKey(ProviderType)
    patient = models.ForeignKey(Patient)

    written_datetime = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class DocumentType(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name


class Document(Note):
    title = models.CharField(max_length=200)
    image = models.FileField(
        help_text="Please deidentify all file names before upload! Delete all files after upload!",
        upload_to=make_filepath,
        verbose_name="PDF File or Image Upload")
    comments = models.TextField()
    document_type = models.ForeignKey(DocumentType)

    history = HistoricalRecords()

    def short_text(self):
        return self.title


class CompletableManager(models.Manager):
    """ Class that handles queryset filers for Completable classes."""

    def get_active(self, patient):
        """ Returns all active elements of Completable class."""
        return self.get_queryset()\
                .filter(patient=patient)\
                .filter(completion_author=None)\
                .filter(due_date__lte=now().date())\
                .order_by('completion_date')

    def get_inactive(self, patient):
        """ Returns all inactive elements of Completable class."""
        return self.get_queryset()\
                .filter(patient=patient)\
                .filter(completion_author=None)\
                .filter(due_date__gt=now().date())\
                .order_by('completion_date')

    def get_completed(self, patient):
        """ Returns all completed elements of Completable class."""
        return self.get_queryset()\
                .filter(patient=patient)\
                .exclude(completion_author=None)\
                .order_by('completion_date')

class CompletableMixin(models.Model):
    """CompleteableMixin is for anything that goes in that list of
    stuff on the Patient detail page. They can be marked as
    complete.
    """

    class Meta:
        abstract = True

    objects = CompletableManager()

    completion_date = models.DateTimeField(blank=True, null=True)
    completion_author = models.ForeignKey(
        Provider,
        blank=True, null=True,
        related_name="%(app_label)s_%(class)s_completed")
    due_date = models.DateField(help_text="MM/DD/YYYY or YYYY-MM-DD")

    def done(self):
        """Return true if this ActionItem has been marked as done."""
        return self.completion_date is not None

    def mark_done(self, provider):
        self.completion_date = now()
        self.completion_author = provider

    def clear_done(self):
        self.completion_author = None
        self.completion_date = None


class ActionItem(Note, CompletableMixin):
    instruction = models.ForeignKey(ActionInstruction)
    priority = models.BooleanField(
        default=False,
        help_text='Check this box if this action item is high priority')
    comments = models.TextField()

    history = HistoricalRecords()

    def class_name(self):
        return self.__class__.__name__

    def attribution(self):
        if self.done():
            return " ".join(["Marked done by", str(self.completion_author),
                             "on", str(self.completion_date.date())])
        else:
            return " ".join(["Added by", str(self.author), "on",
                             str(self.written_datetime.date())])

    def __unicode__(self):
        return " ".join(["AI for", str(self.patient)+":",
                         str(self.instruction), "due on", str(self.due_date)])
