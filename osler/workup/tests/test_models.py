from __future__ import unicode_literals
from django.test import TestCase
from django.utils.timezone import now

from osler.core.models import Patient
from osler.core.tests.test_views import build_user

from osler.workup import models
from osler.workup.tests.tests import wu_dict, note_dict

import osler.users.tests.factories as user_factories


class TestAttestations(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):

        self.wu = models.Workup.objects.create(**wu_dict())
        self.note = models.AttestableBasicNote.objects.create(**note_dict())

    def test_wu_signing(self):
        """test signing permissions """
        self.attestable_note_signing_one_group_test(self.wu)
        self.attestable_note_signing_all_groups_test(self.wu)


    def test_basic_attestable_note_signing(self):
        self.attestable_note_signing_one_group_test(self.note)
        self.attestable_note_signing_all_groups_test(self.note)

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

    def test_pending_wu_signing(self):  
        """Pending workups should not be able to be signed."""

        self.wu.is_pending = True
        self.wu.save()

        user = build_user([user_factories.AttendingGroupFactory])
        group = user.groups.first()

        with self.assertRaises(ValueError):
            self.wu.sign(user, group)

