from __future__ import unicode_literals
from builtins import str
from django.test import TestCase
from django.core import mail
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.management import call_command
from django.utils.timezone import now

from osler.core.tests.test_views import build_user, log_in_user
from osler.core.models import Patient

import osler.users.tests.factories as user_factories

from osler.workup import validators
from osler.workup import models

import factory


def wu_dict(user=None, units=False, clinic_day_pk=False, dx_category=False):

    if not user:
        user = build_user()

    fake_text = 'abc'

    wu = {'clinic_day': models.ClinicDate.objects.first(),
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
          'will_return': True,
          'author': user,
          'author_type': user.groups.first(),
          'patient': Patient.objects.first()
          }

    if units:
        wu['temperature_units'] = 'F'
        wu['weight_units'] = 'lbs'
        wu['height_units'] = 'in'

    if clinic_day_pk:
        wu['clinic_day'] = wu['clinic_day'].pk

    if dx_category:
        wu['diagnosis_categories'] = [models.DiagnosisType.objects.first().pk]

    return wu

def note_dict(user=None):

    if not user:
        user = build_user()

    pn = {
        'title': 'Good',
        'text': 'boy',
        'author': user,
        'author_type': user.groups.first(),
        'patient': Patient.objects.first()
    }

    return pn

class TestEmailForUnsignedNotes(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):

        self.user = build_user([user_factories.AttendingGroupFactory])
        log_in_user(self.client, self.user)

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

    def test_unsigned_email(self):

        pt = Patient.objects.first()

        wu_data = wu_dict(user=self.user)
        wu_data['attending'] = self.user

        wu_signed = models.Workup.objects.create(**wu_data)
        wu_signed.sign(self.user, self.user.groups.first())
        wu_signed.save()

        wu_unsigned = models.Workup.objects.create(**wu_data)

        call_command('unsigned_wu_notify')

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == '[OSLER] 1 Unattested Notes'
        assert str(pt) in mail.outbox[0].body
        assert self.user.last_name in mail.outbox[0].body


        # TODO make this universal

        # self.assertIn(
        #     'https://osler.wustl.edu/workup/%s/' % wu_unsigned.pk,
        #     mail.outbox[0].body)


class TestClinDateViews(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):
        self.provider = log_in_user(
            self.client,
            build_user())

    def test_create_clindate(self):

        pt = Patient.objects.first()

        # First delete clindate that's created in the fixtures.
        models.ClinicDate.objects.all().delete()
        self.assertEqual(models.ClinicDate.objects.count(), 0)

        r = self.client.get(reverse('new-clindate', args=(pt.id,)))
        self.assertEqual(r.status_code, 200)

        r = self.client.post(
            reverse('new-clindate', args=(pt.id,)),
            {'clinic_type': models.ClinicType.objects.first().pk})

        self.assertRedirects(r, reverse('new-workup', args=(pt.id,)))
        self.assertEqual(models.ClinicDate.objects.count(), 1)

        # what happens if we submit twice?
        r = self.client.post(
            reverse('new-clindate', args=(pt.id,)),
            {'clinic_type': models.ClinicType.objects.first().pk})
        self.assertRedirects(r, reverse('new-workup', args=(pt.id,)))
        self.assertEqual(models.ClinicDate.objects.count(), 1)


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

