"""Data models for vaccine system."""

from django.db import models
from django.urls import reverse

from osler.core.models import (Note, AbstractActionItem)
from osler.followup.models import (Followup)


class VaccineSeriesType(models.Model):
    '''Represents type of vaccine (ie. flu shot, hepatitis A, B)'''

    name = models.CharField(max_length=100, primary_key=True)

    def doses(self):
        '''Return queryset of all VaccineDoseTypes for this VaccineSeriesType'''
        return VaccineDoseType.objects.filter(kind=self).order_by('time_from_first')

    def last_dose(self):
        '''Return VaccineDoseType object that is last dose in this VaccineSeriesType'''
        return self.doses().reverse()[0]

    def next_dose(self, dose):
        '''Takes VaccineDoseType and returns next in this VaccineSeriesType or None if last'''
        if dose==self.last_dose():
            return None
        else:
            #Please change if you have a more elegant way of doing
            #Hypothetically shouldn't take forever to query db since shouldn't be too many doses
            for index, item in enumerate(self.doses()):
                if dose==item:
                    return self.doses()[index+1]

    def __str__(self):
        return self.name


class VaccineDoseType(models.Model):
    '''Represents which dose of a given Vaccine Series Type 
    with minimum required time intervals'''

    kind = models.ForeignKey(VaccineSeriesType,
        on_delete=models.CASCADE)
    time_from_first = models.DurationField(default=0, 
        help_text='Example: 60 days for 2 months, input minimum required interval')

    def __str__(self):
        '''Provides string to display on front end for vaccine doses'''
        month = int(self.time_from_first.days/30)
        if month == 0:
            return "%s vaccine first dose" % (self.kind)
        else:
            return "%s vaccine at %s months" % (self.kind, month)


class VaccineSeries(Note):
    '''Record of ordering a patient's vaccine series in clinic'''

    kind = models.ForeignKey(VaccineSeriesType, on_delete=models.PROTECT,
        help_text='What kind of vaccine are you administering?')

    def doses(self):
        '''Return queryset of all VaccineDose for this VaccineSeries'''
        return VaccineDose.objects.filter(series=self).order_by('written_datetime')

    def first_dose(self):
        if not self.doses():
            return None
        else:
            return self.doses()[0]

    def __str__(self):
        return str(self.kind)


class VaccineDose(Note):
    '''Record of administering a patient's particular vaccine dose at clinic.'''

    series = models.ForeignKey(VaccineSeries, on_delete=models.CASCADE,
        help_text='Which vaccine is this?')
    which_dose = models.ForeignKey(VaccineDoseType, on_delete=models.PROTECT)

    def is_last(self):
        '''Return True if this dose is last dose in the series'''
        return self.which_dose==self.series.kind.last_dose()

    def next_due_date(self):
        '''Return DateTime object of next dose due date or None is last dose'''
        if self.is_last():
            return None
        else:
            #Please change if you have a more elegant way of doing
            first = self.series.first_dose() #First VaccineDose in this series
            next = self.series.kind.next_dose(self.which_dose) #Next VaccineDoseType
            next_due=first.written_datetime+next.time_from_first
            return next_due

    def __str__(self):
        return str(self.which_dose)


class VaccineActionItem(AbstractActionItem):
    '''An action item pertaining to vaccine administration (ie calling pt)'''

    vaccine = models.ForeignKey(VaccineSeries, on_delete=models.CASCADE,
        help_text='Which vaccine is this for?')

    MARK_DONE_URL_NAME = 'new-vaccine-followup'

    def short_name(self):
        return "Vaccine"

    def mark_done_url(self):
        return reverse(self.MARK_DONE_URL_NAME,
                       kwargs={'pt_id': self.patient.pk, 'ai_id': self.pk})

    def admin_url(self):
        return reverse('admin:vaccine_vaccineactionitem_change',
                       args=(self.id,))

    def __str__(self):
        formatted_date = self.due_date.strftime("%D")
        return 'Call %s on %s for next dose of %s vaccine' % (self.patient,
                                                    formatted_date,
                                                    self.vaccine)


class VaccineFollowup(Followup):
    '''Datamodel for followup on vaccine action item'''

    action_item = models.ForeignKey(VaccineActionItem, on_delete=models.CASCADE)

    SUBSQ_DOSE_HELP = "Has the patient committed to coming back for another dose?"
    subsq_dose = models.BooleanField(verbose_name=SUBSQ_DOSE_HELP)

    DOSE_DATE_HELP = "When does the patient want to get their next dose (if applicable)?"
    dose_date = models.DateField(blank=True,
                                 null=True,
                                 help_text=DOSE_DATE_HELP)

    def type(self):
        return "Vaccine"

    def short_text(self):
        out = []
        if self.subsq_dose:
            out.append("Patient should return on")
            out.append(str(self.dose_date))
            out.append("for the next dose.")
        else:
            out.append("Patient does not return for another dose.")

        return " ".join(out)
    