from __future__ import unicode_literals
from builtins import str
from django.urls import reverse
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from osler.workup.models import Workup

from collections import defaultdict


class Command(BaseCommand):
    help = '''Email attendings when they have unattested workups.'''

    def handle(self, *args, **options):

        unsigned_wus = Workup.objects.filter(signer=None, attending__isnull=False)
        attending_to_unsigned = defaultdict(list)
        for wu in unsigned_wus:
            attending_to_unsigned[wu.attending].append(wu)

        for attending, wu_list in attending_to_unsigned.items():

            last_name = attending.last_name if attending.last_name else ""

            message_lines = [
                ("Hi there Dr. %s," % last_name),
                '',
                "We've noticed something of a backlog of unattested notes, "
                "and so we've cooked up something to try to "
                "identify--wherever possible--which unattested notes "
                "should have been attested by which physicians. From here, "
                "it looks like the following note(s) should have been "
                "signed by you:",
                ""
            ]

            for wu in wu_list:
                message_lines.append(" ".join([
                    '-', str(wu.patient),
                    '(seen %s):' % wu.clinic_day.clinic_date,
                    'https://osler.wustl.edu' + \
                        reverse('workup', kwargs={'pk': wu.pk})
                    ]))

            message_lines.extend([
                "",
                "Each of these patients' notes should be accessible via the direct link above any time you're on the Barnes/WashU network, or if you're using the VPN. If for some reason you can't access a chart, or you don't think that you were the attending who saw the linked patient, please let me know.",
                "",
                "Cheers,",
                "Justin"
            ])

            send_mail(
                '[OSLER] %s Unattested Notes' % len(wu_list),
                "\n".join(message_lines),
                'jrporter@wustl.edu',
                [attending.email],
                fail_silently=False,
            )
