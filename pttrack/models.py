'''The datamodels for the SNHC clintools patient tracking system'''
from django.db import models
from django.core.exceptions import ValidationError
import django.utils.timezone

# pylint: disable=I0011,missing-docstring,E1305


def validate_zip(value):
    '''verify that the given value is in the ZIP code format'''
    if len(str(value)) != 5:
        raise ValidationError('{0} is not a valid ZIP, because it has {1}' +
                              ' digits.'.format(str(value), len(str(value))))

    if not str(value).isdigit():
        raise ValidationError("%s is not a valid ZIP, because it contains " +
                              "non-digit characters." % value)


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
    short_name = models.CharField(max_length=10)

    def __unicode__(self):
        return self.short_name


class Gender(models.Model):
    long_name = models.CharField(max_length=30)
    short_name = models.CharField(max_length=1)

    def __unicode__(self):
        return self.long_name


class Person(models.Model):

    class Meta:  # pylint: disable=W0232,R0903,C1001
        abstract = True

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=50)

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

    ethnicity = models.ForeignKey(Ethnicity)

    def age(self):
        import datetime
        return (datetime.date.today()-self.date_of_birth).days/365

    def __unicode__(self):
        return self.name()

    def active_action_items(self):
        '''return a list of ActionItems that are 1) not done and
        2) due today or before. The list is sorted by due_date'''

        ai_list = [ai for ai in self.actionitem_set.all() if
                   not ai.done()
                   and ai.due_date <= django.utils.timezone.now().date()]
        ai_list.sort(key=lambda(ai): ai.due_date)
        return ai_list

    def done_action_items(self):
        '''return the set of action items that are done, sorted
        by completion date'''

        ai_list = [ai for ai in self.actionitem_set.all() if ai.done()]
        ai_list.sort(key=lambda(ai): ai.completion_date)

        return ai_list

    def inactive_action_items(self):
        '''return a list of action items that aren't done, but aren't
        due yet either, sorted by due date.'''

        ai_list = [ai for ai in self.actionitem_set.all()
                   if not ai.done()
                   and ai.due_date > django.utils.timezone.now().date()]
        ai_list.sort(key=lambda(ai): ai.due_date)

        return ai_list

    def status(self):
        n_active = len(self.active_action_items())
        n_pending = len(self.inactive_action_items())
        n_done = len(self.done_action_items())

        if n_active > 0:
            return str(n_active)+" action items past due"
        elif n_pending > 0:
            next_item = min(self.inactive_action_items(),
                            key=lambda(k): k.due_date)
            tdelta = next_item.due_date - django.utils.timezone.now().date()
            return "next action in "+str(tdelta.days)+" days"
        elif n_done > 0:
            return "all actions complete"
        else:
            return "no pending actions"

    def notes(self):
        note_list = list(self.workup_set.all())
        # note_list.extend(self.followup_set.all())
        note_list.sort(key=lambda(k): k.written_date)

        return note_list


class Provider(Person):

    email = models.EmailField()

    def __unicode__(self):
        return self.name()


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


class Note(models.Model):
    class Meta:  # pylint: disable=W0232,R0903,C1001
        abstract = True

    author = models.ForeignKey(Provider)
    author_type = models.ForeignKey(ProviderType)
    patient = models.ForeignKey(Patient)


# class Documents(Note):
#     image
#     comments
#     title
#     upload type (i.e. lab, prescription)


class ActionItem(Note):
    written_date = models.DateTimeField(default=django.utils.timezone.now)
    due_date = models.DateField()
    comments = models.CharField(max_length=300)
    instruction = models.ForeignKey(ActionInstruction)
    completion_date = models.DateTimeField(blank=True, null=True)
    completion_author = models.ForeignKey(Provider,
                                          blank=True,
                                          null=True,
                                          related_name="action_items_completed"
                                         )

    def mark_done(self, provider):
        self.completion_date = django.utils.timezone.now()
        self.completion_author = provider

    def clear_done(self):
        self.completion_author = None
        self.completion_date = None

    def done(self):
        '''Returns true if this ActionItem has been marked as done'''
        return self.completion_date is not None

    def attribution(self):
        if self.done():
            return " ".join(["Marked done by", str(self.completion_author),
                             "on", str(self.completion_date.date())])
        else:
            return " ".join(["Added by", str(self.author), "on",
                             str(self.written_date.date())])

    def __unicode__(self):
        return "AI: "+str(self.instruction)+" on "+str(self.due_date)


class Workup(Note):
    clinic_day = models.ForeignKey(ClinicDate)

    chief_complaint = models.CharField(max_length=300)

    HandP = models.TextField()
    AandP = models.TextField()

    diagnosis = models.CharField(max_length=100)

    def short_text(self):
        return self.chief_complaint

    def written_date(self):
        return self.clinic_day.clinic_date

    def attribution(self):
        return " ".join([str(self.author), "on", str(self.written_date())])

    def __unicode__(self):
        return self.patient.name()+" on "+str(self.clinic_day.clinic_date)
