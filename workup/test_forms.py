import decimal

from django.test import TestCase

from pttrack.models import Provider, ProviderType, Gender

from .models import DiagnosisType, ClinicDate, ClinicType
from .forms import WorkupForm

from .tests import wu_dict


class TestHelperFunctions(TestCase):

    def test_unit_converter_helpers_accept_None(self):
        from . import forms

        self.assertEqual(
            forms.fahrenheit2centigrade(None), None)
        self.assertEqual(
            forms.pounds2kilos(None), None)
        self.assertEqual(
            forms.inches2cm(None), None)


class TestWorkupFormUnitAwareFields(TestCase):

    def setUp(self):
        DiagnosisType.objects.create(name='Cardiovascular')
        ClinicType.objects.create(name='Main Clinic')
        ClinicDate.objects.create(
            clinic_date='2018-08-26', clinic_type=ClinicType.objects.first())

        wu_data = wu_dict()
        wu_data['diagnosis_categories'] = [DiagnosisType.objects.first().pk]
        wu_data['clinic_day'] = wu_data['clinic_day'].pk
        wu_data['got_imaging_voucher'] = False
        wu_data['got_voucher'] = False

        del wu_data['t']

        # this wu_data object should have specified _none_ of the fields
        # for unit-aware vital signs
        self.wu_data = wu_data

    def test_vitals_no_units_error(self):
        """If vitals measurement w/o units, raise error"""

        for field, value in [('t', 98.6),
                             ('height', 100),
                             ('weight', 180)]:

            wu_data = self.wu_data.copy()
            wu_data[field] = value

            form = WorkupForm(data=wu_data)
            self.assertFalse(
                form.is_valid(),
                msg='Failed to raise error if only %s specified' % field)
            self.assertNotEqual(form[field].errors, [])

    def test_vitals_no_value_no_units_ok(self):
        """Units are required only when vitals are provided."""

        form = WorkupForm(data=self.wu_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_note_temp_conversion(self):

        wu_data = self.wu_data

        # temperatures with centigrade should be the same
        wu_data['temperature_units'] = 'C'
        wu_data['t'] = 37

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEquals(
            form.cleaned_data['t'],
            wu_data['t'])

        # temperatures given centigrade should be converted
        wu_data['temperature_units'] = 'F'
        wu_data['t'] = 98
        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEquals(
            round((wu_data['t'] - 32) * decimal.Decimal(5 / 9.0)),
            round(decimal.Decimal(form.cleaned_data['t'])))

    def test_note_height_conversion(self):

        wu_data = self.wu_data

        # heights with cm should be the same
        wu_data['height_units'] = 'cm'
        wu_data['height'] = 180

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEquals(
            form.cleaned_data['height'],
            wu_data['height'])

        # heights given inches should be converted
        wu_data['height_units'] = 'in'
        wu_data['height'] = 71

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEquals(
            form.cleaned_data['height'],
            round(wu_data['height'] * decimal.Decimal(2.54), 0))

    def test_note_weight_conversion(self):

        wu_data = self.wu_data

        # weights with kilograms should be the same
        wu_data['weight_units'] = 'kg'
        wu_data['weight'] = 81

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEquals(
            form.cleaned_data['weight'],
            wu_data['weight'])

        # weights given lbs should be converted
        wu_data['weight_units'] = 'lbs'

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEquals(
            round(form.cleaned_data['weight']),
            round(wu_data['weight'] / decimal.Decimal(2.2)))


class TestWorkupFormValidators(TestCase):

    fixtures = ['workup', 'pttrack']

    def setUp(self):
        self.valid_wu_dict = wu_dict()

    def test_blood_pressure_together(self):
        """Systolic and diastolic bp must be specified together."""

        form_data = self.valid_wu_dict.copy()
        del form_data['bp_sys']

        form = WorkupForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data = self.valid_wu_dict.copy()
        del form_data['bp_dia']

        form = WorkupForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_blood_pressure(self):

        form_data = self.valid_wu_dict
        form = WorkupForm(data=form_data)

        self.assertEqual(form['bp_sys'].errors, [])
        self.assertEqual(form['bp_dia'].errors, [])

        form_data['bp_sys'] = '800'

        form = WorkupForm(data=form_data)
        self.assertNotEqual(form['bp_sys'].errors, [])

        form_data['bp_sys'] = '120'
        form_data['bp_dia'] = '30'

        form = WorkupForm(data=form_data)
        self.assertNotEqual(form['bp_dia'].errors, [])

        # the systolic < diastolic error is a bp_sys error not bp_dia
        form_data['bp_dia'] = '130'
        form = WorkupForm(data=form_data)
        self.assertNotEqual(form['bp_sys'].errors, [])

    def test_missing_voucher_amount(self):

        form_data = self.valid_wu_dict
        form_data['got_voucher'] = True
        form_data['got_imaging_voucher'] = True

        form = WorkupForm(data=form_data)

        self.assertNotEqual(form['voucher_amount'].errors, [])
        self.assertNotEqual(form['patient_pays'].errors, [])

        form_data['voucher_amount'] = '40'
        form_data['patient_pays'] = '40'

        form = WorkupForm(data=form_data)
        self.assertEqual(form['voucher_amount'].errors, [])
        self.assertEqual(form['patient_pays'].errors, [])

        self.assertNotEqual(form['imaging_voucher_amount'].errors, [])
        self.assertNotEqual(form['patient_pays_imaging'].errors, [])

        form_data['imaging_voucher_amount'] = '40'
        form_data['patient_pays_imaging'] = '40'

        form = WorkupForm(data=form_data)
        self.assertEqual(form['imaging_voucher_amount'].errors, [])
        self.assertEqual(form['patient_pays_imaging'].errors, [])


class TestWorkupFormProviderChoices(TestCase):

    def setUp(self):
        Gender.objects.create(short_name='A', long_name="Alien")

        attending = ProviderType.objects.create(
            long_name='Attending Physician', short_name='AP',
            signs_charts=True, staff_view=True)

        coordinator = ProviderType.objects.create(
            long_name='Coordinator', short_name='C',
            signs_charts=False, staff_view=True)

        volunteer = ProviderType.objects.create(
            long_name='Volunteer', short_name='V',
            signs_charts=False, staff_view=False)

        provider_skeleton = {
            'first_name': "Firstname",
            'last_name': "Lastname",
            'gender': Gender.objects.first(),
        }

        pvds = [Provider.objects.create(
            middle_name=str(i), **provider_skeleton) for i in range(4)]
        pvds[1].clinical_roles.add(attending)
        pvds[2].clinical_roles.add(coordinator)
        pvds[3].clinical_roles.add(volunteer)
        [p.save() for p in pvds]

        self.pvds = pvds
        self.form = WorkupForm()

    def test_form_attending_options(self):
        """WorkupForm offers only attending Providers for 'attending'"""

        cm_qs = Provider.objects.filter(
            clinical_roles__in=ProviderType.objects.filter(
                signs_charts=True)).values_list('id', flat=True)

        # c[0] is the pk of each, [1:] indexing required because element 0
        # is the "blank" option.
        form_list = [c[0] for c in self.form['attending'].field.choices][1:]

        # cast to set for 1) order-insensitivity and 2) b/c cm_qs is
        # a queryset and form_list is a list
        self.assertEqual(set(cm_qs), set(form_list))

        # Make sure we reject non-attending providers
        form_data = wu_dict()
        form_data['attending'] = self.pvds[2].pk
        form = WorkupForm(data=form_data)
        self.assertNotEqual(form['attending'].errors, [])

        form_data['attending'] = self.pvds[3].pk
        form = WorkupForm(data=form_data)
        self.assertNotEqual(form['attending'].errors, [])

        # Make sure we accept attending providers
        form_data['attending'] = self.pvds[1].pk
        form = WorkupForm(data=form_data)
        self.assertEqual(form['attending'].errors, [])

    def test_form_other_volunteer_options(self):
        """WorkupForm offers only non-attendings for 'other volunteers'"""

        cm_qs = Provider.objects.filter(
            clinical_roles__in=ProviderType.objects.filter(
                signs_charts=False)).values_list('id', flat=True)
        form_list = [c[0] for c in self.form['other_volunteer'].field.choices]

        self.assertEqual(set(cm_qs), set(form_list))

        # Reject attending providers
        form_data = wu_dict()
        form_data['other_volunteer'] = self.pvds[1].pk
        form = WorkupForm(data=form_data)
        self.assertNotEqual(form['other_volunteer'].errors, [])

        # Accept non-attending providers
        form_data['other_volunteer'] = [self.pvds[2].pk]
        form = WorkupForm(data=form_data)
        self.assertEqual(form['other_volunteer'].errors, [])

        form_data['other_volunteer'] = [self.pvds[3].pk]
        form = WorkupForm(data=form_data)
        self.assertEqual(form['other_volunteer'].errors, [])
