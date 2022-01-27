from __future__ import unicode_literals
from builtins import str
from django.test import TestCase
from django.core import mail
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.management import call_command
from django.utils.timezone import now

from osler.core.tests.test_views import build_user, log_in_user
from osler.core.models import Patient, Encounter, EncounterStatus

import osler.users.tests.factories as user_factories
import osler.core.tests.factories as core_factories

from osler.workup import validators
from osler.workup import models
from osler.workup.tests import factories as workup_factories

import factory


def wu_dict(user=None, units=False, dx_category=False):

    if not user:
        user = build_user()

    fake_text = 'abc'

    pt = core_factories.PatientFactory()
    status = core_factories.EncounterStatusFactory()

    e = Encounter.objects.create(
       patient=pt,
       clinic_day=now().date(),
       status=status)

    wu = {'encounter': e,
          'chief_complaint': "SOB",
          'diagnosis': "MI",
          'hpi': fake_text,
          'pmh': fake_text,
          'psh': fake_text,
          'meds': fake_text,
          'allergies': fake_text,
          'fam_hx': fake_text,
          'soc_hx': fake_text,
          'ros': "f", 'pe': "f", 'a_and_p': "f",
          'hr': '89', 'bp_sys': '120', 'bp_dia': '80', 'rr': '16', 't': '98',
          'labs_ordered_internal': 'f', 'labs_ordered_external': 'f',
          'got_voucher': False,
          'got_imaging_voucher': False,
          'author': user,
          'author_type': user.groups.first(),
          'patient': pt
          }

    if units:
       wu['temperature_units'] = 'F'
       wu['weight_units'] = 'lbs'
       wu['height_units'] = 'in'

    if dx_category:
       wu['diagnosis_categories'] = [models.DiagnosisType.objects.first().pk]

    return wu

def note_dict(user=None, encounter_pk=True):

    pt = core_factories.PatientFactory()
    status = core_factories.EncounterStatusFactory()

    if not user:
        user = build_user()

    pn = {
        'title': 'Good',
        'text': 'boy',
        'author': user,
        'author_type': user.groups.first(),
        'patient': pt
    }

    if encounter_pk:
        pn['encounter'] = Encounter.objects.create(
            patient=pt,
            clinic_day=now().date(),
            status=status)

    return pn

class TestEmailForUnsignedNotes(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):

        self.user = build_user([user_factories.AttendingGroupFactory])
        log_in_user(self.client, self.user)

    def test_unsigned_email(self):



        pt = core_factories.PatientFactory()
    
        wu_signed = workup_factories.WorkupFactory(attending = self.user)

        wu_signed.sign(self.user, self.user.groups.first())
        wu_signed.save()

        wu_unsigned = workup_factories.WorkupFactory(attending = self.user)
       
        call_command('unsigned_wu_notify')
        print(mail.outbox[0].subject)

        assert len(mail.outbox) == 1
        print(mail.outbox[0].subject)

        assert mail.outbox[0].subject == '[OSLER] 1 Unattested Notes'
        
        assert self.user.last_name in mail.outbox[0].body


        # TODO make this universal

class TestWorkupFieldValidators(TestCase):
    '''
    TestCase to verify that validators are functioning.
    '''

    def test_validate_hr(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_hr("100"), None)
        self.assertEqual(validators.validate_hr("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_hr("902/")
        with self.assertRaises(ValidationError):
            validators.validate_hr("..90")
        with self.assertRaises(ValidationError):
            validators.validate_hr("93.232")

    def test_validate_rr(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_rr("100"), None)
        self.assertEqual(validators.validate_rr("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_rr("90/")
        with self.assertRaises(ValidationError):
            validators.validate_rr("..90")
        with self.assertRaises(ValidationError):
            validators.validate_rr("93.232")

    def test_validate_t(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_t("100.11"), None)
        self.assertEqual(validators.validate_t("90.21"), None)

        with self.assertRaises(ValidationError):
            validators.validate_t("90x")

    def test_validate_height(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_height("100"), None)
        self.assertEqual(validators.validate_height("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_height("90x")
        with self.assertRaises(ValidationError):
            validators.validate_height("90.0")
        with self.assertRaises(ValidationError):
            validators.validate_height("93.232")

    def test_validate_weight(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_weight("100"), None)
        self.assertEqual(validators.validate_weight("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_weight("90x")
        with self.assertRaises(ValidationError):
            validators.validate_weight("9.0")
        with self.assertRaises(ValidationError):
            validators.validate_weight("93.232")

