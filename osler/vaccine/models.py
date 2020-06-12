"""Data models for vaccine system."""

from django.db import models

from osler.core.models import Note #, ActionItem)
# from osler.followup.models import (Followup)


class VaccineSeriesType(models.Model):
	'''Represents type of vaccine (ie. flu shot, hepatitis A, B)'''

	name = models.CharField(max_length=100, primary_key=True)

	def __str__(self):
		return self.name


class VaccineDoseType(models.Model):
	'''Represents which dose of a given Vaccine Series Type 
	with minimum required time intervals'''

	kind = models.ForeignKey(VaccineSeriesType,
		on_delete=models.CASCADE)
	time_from_first = models.DurationField(default=0, 
		help_text='Example: 60 days for 2 months, input minimum required interval')

	def time_in_months(self):
		'''Returns time_from_first, a timedelta object, in integer months'''
		#The greatest duration stored is days
		return self.time_from_first.days/30

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

	def __str__(self):
		return str(self.kind)


class VaccineDose(Note):
	'''Record of administering a patient's particular vaccine dose at clinic.'''

	series = models.ForeignKey(VaccineSeries, on_delete=models.CASCADE,
		help_text='Which vaccine is this?')
	which_dose = models.ForeignKey(VaccineDoseType, on_delete=models.PROTECT)

	def __str__(self):
		return str(self.which_dose)


# class VaccineActionItem(ActionItem):
# 	'''An action item pertaining to vaccine administration (ie calling pt)'''

# 	vaccine = models.ForeignKey(VaccineSeries, on_delete=models.CASCADE,
# 		help_text='Which vaccine is this for?')

# 	MARK_DONE_URL_NAME = 'new-vaccine-followup'

# 	def short_name(self):
# 		return "Vaccine"

# 	def mark_done_url(self):
#         return reverse(self.MARK_DONE_URL_NAME,
#                        args=(self.id,))

#     def admin_url(self):
#         return reverse('admin:vaccine_vaccineactionitem_change',
#                        args=(self.id,))

#     def __str__(self):
#     	formatted_date = self.due_date.strftime("%D")
#         return 'Call %s on %s for next dose of %s vaccine' % (self.patient,
#                                                     formatted_date,
#                                                     self.vaccine)


# class VaccineFollowup(Followup):
# 	'''Datamodel for followup on vaccine action item'''

# 	action_item = models.ForeignKey(VaccineActionItem, on_delete=models.CASCADE)

# 	SUBSQ_DOSE_HELP = "Has the patient committed to coming back for another dose?"
#     subsq_dose = models.BooleanField(verbose_name=SUBSQ_DOSE_HELP)

#     DOSE_DATE_HELP = "When does the patient want to get their next dose (if applicable)?"
#     dose_date = models.DateField(blank=True,
#                                  null=True,
#                                  help_text=DOSE_DATE_HELP)

# 	def type(self):
# 		return "Vaccine"

# 	def short_text(self):
#         out = []
#         if self.subsq_dose:
#             out.append("Patient should return on")
#             out.append(str(self.dose_date))
#             out.append("for the next dose.")
#         else:
#             out.append("Patient does not return for another dose.")

#         return " ".join(out)
	