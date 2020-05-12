from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
import django.utils.timezone
from osler.core import models

class Command(BaseCommand):
	help = '''Sends email to case managers or author of the action item 
	when action item is due...currently everyday?'''

	def handle(self, *args, **options):
		providerEmails = []
		#all action items that are past due and incomplete
		actionItemList = models.ActionItem.objects.filter(due_date__lte=django.utils.timezone.now().date()).filter(completion_date=None)
		for actionItem in actionItemList:
			try:
				for coordinator in actionItem.patient.case_managers.all():
					email = coordinator.associated_user.email
					if email not in providerEmails:
						providerEmails = providerEmails + [email]
			except AttributeError:
				pass
		message = '''Hello Case Manager! You have an action item due. Please do it otherwise you will
		 continue to be spammed. Thanks! If you are recieving this message but you really don't have
		 an action item due, please contact your current Tech Tsar to relieve you of your misery.'''
		email = EmailMessage('SNHC: Action Item Due', message, to=providerEmails)
		email.send()

