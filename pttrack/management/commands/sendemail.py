from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
import django.utils.timezone
from pttrack import models

class Command(BaseCommand):
	help = "Sends email when Action Item is due"

	def handle(self, *args, **options):
		providerEmails = []
		actionItemList = models.ActionItem.objects.filter(due_date__lte=django.utils.timezone.now().date())
		for actionItem in actionItemList:
			self.stdout.write('there are items in the list')
			#if actionItem.due_date == django.utils.timezone.now().date():
			try:
				email =  actionItem.patient.case_manager.associated_user.email
			except ValueError:
				email = actionItem.author.associated_user.email
			if email not in providerEmails:
				providerEmails.extend(email)			
		message = "Hello, you have an action item due today. Please do it otherwise I will be asked to automate reminders which I don't want to do. Thanks!"
		send_mail('Action Item Due', message, "webmaster@osler.wustl.edu", providerEmails, fail_silently=False)
