from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
import django.utils.timezone

from osler.core import models


class Command(BaseCommand):
    help = """Sends email to case managers or author of the action item
    when action item is due...currently every day?"""

    def handle(self, *args, **options):
        provider_emails = set()

        # all action items that are past due and incomplete
        ai_list = models.ActionItem.objects.filter(
            due_date__lte=django.utils.timezone.now().date()
        ).filter(completion_date__isnull=True)

        for ai in ai_list:

            print(ai)
            for coordinator in ai.patient.case_managers.all():
                email = coordinator.email
                if email not in provider_emails:
                    provider_emails.add(email)

        message = (
            "Hello Case Manager! You have an action item due. Please do "
            "it otherwise you will continue to be spammed. Thanks! If you "
            "are recieving this message but you really don't have an "
            "action item due, please contact your current Tech Tsar to "
            "relieve you of your misery."""
        )

        email = EmailMessage(
            'SNHC: Action Item Due', message, to=provider_emails)
        email.send()
