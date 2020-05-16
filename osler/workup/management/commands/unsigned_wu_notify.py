from __future__ import unicode_literals
from builtins import str
from django.urls import reverse
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from osler.core.models import Provider
from osler.workup.models import Workup


class Command(BaseCommand):
    help = '''Email attendings when they have unattested workups.'''

    def handle(self, *args, **options):

        unsigned_wus = Workup.objects.filter(signer=None)

        # print(unsigned_wus)

        unsigned_wu2providers = {
            wu: Provider.objects.filter(
                signed_workups__in=wu.clinic_day.workup_set.all()).first()
            for wu in unsigned_wus}

        provider2unsigned = {}
        uninferred = []
        for unsigned_wu, provider in list(unsigned_wu2providers.items()):
            if provider is not None:
                if provider in provider2unsigned:
                    provider2unsigned[provider].append(unsigned_wu)
                else:
                    provider2unsigned[provider] = [unsigned_wu]
            else:
                uninferred.append(unsigned_wu)

        # print(provider2unsigned)

        for provider, inferred_wus in list(provider2unsigned.items()):

            last_name = (provider.last_name if provider.last_name
                         else provider.associated_user.last_name)

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

            for wu in inferred_wus:
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
                '[OSLER] %s Unattested Notes' % len(inferred_wus),
                "\n".join(message_lines),
                'jrporter@wustl.edu',
                [provider.associated_user.email],
                fail_silently=False,
            )
