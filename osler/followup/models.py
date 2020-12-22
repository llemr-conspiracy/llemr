'''The datamodels for various types required for followup tracking in Osler.'''
from django.db import models
from osler.core.models import (Note, ContactMethod,
                                  ReferralType, ReferralLocation, ActionItem)

from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _

class NoShowReason(models.Model):
    '''Simple text-contiaining class for storing the different reasons a
    patient might not have gone to a scheduled appointment.'''

    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class NoAptReason(models.Model):
    '''Simple text-contiaining class for storing the different kinds of
    clinics a patient can be referred to (e.g. PCP, ortho, etc.)'''

    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class ContactResult(models.Model):
    '''Abstract base model for representing the resolution to a followup
    attempt with a patient (e.g. no answer w/ voicemail).'''

    name = models.CharField(max_length=100, primary_key=True)
    attempt_again = models.BooleanField(
        default=False,
        verbose_name=_("Attempt again"),
        help_text=_("True if outcome means the pt should be contacted again."))
    patient_reached = models.BooleanField(
        default=True,
        verbose_name=_("Patient reached"),
        help_text=_("True if outcome means they reached the patient"))

    def __str__(self):
        return self.name


class Followup(Note):
    '''The base followup class used in all different types of patient followup
    notes. Can also be instantiated as a 'general follouwp' type.'''

    class Meta(object):
        abstract = True

    contact_method = models.ForeignKey(
        ContactMethod, on_delete=models.PROTECT, verbose_name=_("Contact method"))
    contact_resolution = models.ForeignKey(
        ContactResult, on_delete=models.PROTECT, verbose_name=_("Contact resolution"))

    comments = models.TextField(blank=True, null=True)

    def type(self):
        '''Returns a short string value used as a key to determine which type
        of followup note this is. Human readable.'''

        # in a brutally ugly turn of events, there doesn't appear to be a good
        # way to overridde this method in subclasses. Behold the hacky result:
        for child in ["labfollowup","actionitemfollowup"]:
            # you may ask "where did those strings come from?" or "how do you
            # know that it's all lower case?"... MYSTERIES FOR THE AGES.
            if hasattr(self, child):
                return getattr(self, child).type()

        return _("General")

    def short_text(self):
        '''Return a short text description of this followup and what happened.
        Used on the patient chart view as the text in the list of followups.'''

        return self.comments

    def attribution(self):
        '''Returns a string that is used as the attribution (i.e. "John at
        4pm") for this note.'''
        return " ".join([self.author.name(), _("on"), str(self.written_date())])

    def written_date(self):
        '''Returns a python date object for when this followup was written.'''
        return self.written_datetime.date()

    def __str__(self):
        return " ".join([_("Followup for "), self.patient.name(), _(" on "),
                         str(self.written_date())])


class ActionItemFollowup(Followup):
    '''Datamodel for a action item followup. '''
    history = HistoricalRecords()

    action_item = models.ForeignKey(
        ActionItem,
        verbose_name=_("Action item"),
        on_delete=models.CASCADE)

    def type(self):
        return "Action Item"
