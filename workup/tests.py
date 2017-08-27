from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from pttrack.test_views import build_provider, log_in_provider
from pttrack.models import Patient, ProviderType, Provider

from . import validators
from . import models


def wu_dict(units=False):
    wu = {
            'clinic_day': models.ClinicDate.objects.first(),
            'chief_complaint': "SOB",
            'diagnosis': "MI",
            'HPI': "f", 'PMH_PSH': "f", 'meds': "f", 'allergies': "f",
            'fam_hx': "f", 'soc_hx': "f",
            'ros': "f", 'pe': "f", 'A_and_P': "f",
            'hr': '89', 'bp_sys': '120', 'bp_dia': '80', 'rr': '16', 't': '98',
            'labs_ordered_internal': 'f', 'labs_ordered_quest': 'f',
            'got_voucher': False,
            'got_imaging_voucher': False,
            'will_return': True,
            'author': Provider.objects.first(),
            'author_type': ProviderType.objects.first(),
            'patient': Patient.objects.first()
        }

    if units:
        wu['temperature_units'] = 'F'
        wu['weight_units'] = 'lbs'
        wu['height_units'] = 'in'

    return wu


class TestClinDateViews(TestCase):

    fixtures = ['workup', 'pttrack']

    def setUp(self):
        self.provider = log_in_provider(
            self.client,
            build_provider())

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


class TestWorkupModel(TestCase):

    fixtures = ['workup', 'pttrack']

    def setUp(self):
        self.provider = log_in_provider(
            self.client,
            build_provider())

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date(),
            gcal_id="tmp")

        self.valid_wu_dict = wu_dict()

    def test_sign(self):

        wu = models.Workup.objects.create(**self.valid_wu_dict)

        # attempt sign as non-attending
        disallowed_ptype = ProviderType.objects.\
            filter(signs_charts=False).first()
        with self.assertRaises(ValueError):
            wu.sign(
                self.provider.associated_user,
                disallowed_ptype)
        wu.save()

        # attempt sign without missing ProviderType
        unassociated_ptype = ProviderType.objects.create(
            long_name="New", short_name="New", signs_charts=True)
        with self.assertRaises(ValueError):
            wu.sign(
                self.provider.associated_user,
                unassociated_ptype)

        # attempt sign as attending
        allowed_ptype = ProviderType.objects.\
            filter(signs_charts=True).first()
        wu.sign(
            self.provider.associated_user,
            allowed_ptype)
        wu.save()
