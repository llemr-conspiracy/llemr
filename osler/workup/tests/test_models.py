from __future__ import unicode_literals
from django.test import TestCase
from django.utils.timezone import now

from osler.core.models import Patient
from osler.core.tests.test_views import build_user

from osler.workup import models
from osler.workup.tests.tests import wu_dict, pn_dict

import osler.users.tests.factories as user_factories


class TestAttestations(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

        self.wu = models.Workup.objects.create(**wu_dict())
        self.pn = models.AttestableBasicNote.objects.create(**pn_dict())

    def test_wu_signing(self):
        """test signing permissions """
        self.attestable_note_signing_one_group_test(self.wu)
        self.attestable_note_signing_all_groups_test(self.wu)


    def test_pn_signing(self):
        self.attestable_note_signing_one_group_test(self.pn)
        self.attestable_note_signing_all_groups_test(self.pn)

    def attestable_note_signing_one_group_test(self, note):  
        """test signing permissions for attestable note
        when user has one group."""

        for role in user_factories.all_roles:
            user = build_user([role])
            group = user.groups.first()

            # attending can sign
            if role in user_factories.attesting_roles:
                note.sign(user, group)
                assert note.signed()

            else:  
                # non-attending can't sign
                with self.assertRaises(ValueError):
                    note.sign(user, group)
                assert not note.signed()

                # non-attending can't use another group to sign
                with self.assertRaises(ValueError):
                    note.sign(user, user_factories.AttendingGroupFactory())
                assert not note.signed()

            # reset chart's signed status
            note.signer = None

    def attestable_note_signing_all_groups_test(self, note):
        """Check that signing permission depend on only the
        supplied group."""

        user = build_user(user_factories.all_roles)
        for group in user.groups.all():

            # should be able to sign
            if note.group_can_sign(group):
                note.sign(user, group)
                assert note.signed()

            # should not be able to sign
            else:
                with self.assertRaises(ValueError):
                    note.sign(user, group)
                assert not note.signed()

            note.signer = None

        

