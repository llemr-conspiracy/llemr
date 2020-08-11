from __future__ import division
from __future__ import unicode_literals
from builtins import str
from builtins import range
from past.utils import old_div
import decimal

from django.test import TestCase

from osler.core.models import Gender

from osler.workup.models import DiagnosisType, ClinicDate, ClinicType, Workup
from osler.workup.forms import WorkupForm

from osler.workup.tests import wu_dict, pn_dict

from osler.core.tests.test_views import build_user
import osler.users.tests.factories as user_factories

from itertools import chain, combinations


class TestHelperFunctions(TestCase):

    def test_unit_converter_helpers_accept_None(self):
        from osler.workup import forms

        unit_converters = [
            forms.fahrenheit2centigrade,
            forms.pounds2kilos,
            forms.inches2cm
        ]
        for unit_converter in unit_converters:
            assert not unit_converter(None)

class TestWorkupFormUnitAwareFields(TestCase):

    # fixtures = ['core', 'workup']

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
            self.assertNotEqual(len(form[field].errors), 0)

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
        self.assertEqual(
            form.cleaned_data['t'],
            wu_data['t'])

        # temperatures given centigrade should be converted
        wu_data['temperature_units'] = 'F'
        wu_data['t'] = 98
        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            round((wu_data['t'] - 32) * decimal.Decimal(5 / 9.0)),
            round(decimal.Decimal(form.cleaned_data['t'])))

    def test_note_height_conversion(self):

        wu_data = self.wu_data

        # heights with cm should be the same
        wu_data['height_units'] = 'cm'
        wu_data['height'] = 180

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            form.cleaned_data['height'],
            wu_data['height'])

        # heights given inches should be converted
        wu_data['height_units'] = 'in'
        wu_data['height'] = 71

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            form.cleaned_data['height'],
            round(wu_data['height'] * decimal.Decimal(2.54), 0))

    def test_note_weight_conversion(self):

        wu_data = self.wu_data

        # weights with kilograms should be the same
        wu_data['weight_units'] = 'kg'
        wu_data['weight'] = 81

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            form.cleaned_data['weight'],
            wu_data['weight'])

        # weights given lbs should be converted
        wu_data['weight_units'] = 'lbs'

        form = WorkupForm(data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            round(form.cleaned_data['weight']),
            round(old_div(wu_data['weight'], decimal.Decimal(2.2))))


class TestWorkupFormValidators(TestCase):

    fixtures = ['workup', 'core']

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

        self.assertEqual(len(form['bp_sys'].errors), 0)
        self.assertEqual(len(form['bp_dia'].errors), 0)

        form_data['bp_sys'] = '800'

        form = WorkupForm(data=form_data)
        self.assertNotEqual(len(form['bp_sys'].errors), 0)

        form_data['bp_sys'] = '120'
        form_data['bp_dia'] = '30'

        form = WorkupForm(data=form_data)
        self.assertNotEqual(len(form['bp_dia'].errors), 0)

        # the systolic < diastolic error is a bp_sys error not bp_dia
        form_data['bp_dia'] = '130'
        form = WorkupForm(data=form_data)
        self.assertNotEqual(len(form['bp_sys'].errors), 0)

    def test_missing_voucher_amount(self):

        form_data = self.valid_wu_dict
        form_data['got_voucher'] = True
        form_data['got_imaging_voucher'] = True

        form = WorkupForm(data=form_data)

        self.assertNotEqual(len(form['voucher_amount'].errors), 0)
        self.assertNotEqual(len(form['patient_pays'].errors), 0)

        form_data['voucher_amount'] = '40'
        form_data['patient_pays'] = '40'

        form = WorkupForm(data=form_data)
        self.assertEqual(len(form['voucher_amount'].errors), 0)
        self.assertEqual(len(form['patient_pays'].errors), 0)

        self.assertNotEqual(len(form['imaging_voucher_amount'].errors), 0)
        self.assertNotEqual(len(form['patient_pays_imaging'].errors), 0)

        form_data['imaging_voucher_amount'] = '40'
        form_data['patient_pays_imaging'] = '40'

        form = WorkupForm(data=form_data)
        self.assertEqual(len(form['imaging_voucher_amount'].errors), 0)
        self.assertEqual(len(form['patient_pays_imaging'].errors), 0)


class TestWorkupFormProviderChoices(TestCase):

    def setUp(self):

        # build large list of users with different combinations of roles
        self.users = []
        role_list = list(user_factories.all_roles)
        role_powerset = chain.from_iterable(
            combinations(role_list, r) for r in range(1, len(role_list)+1))
        for role_tuple in role_powerset:
            for _ in range(3):
                self.users.append(build_user(list(role_tuple)))

    def test_form_attending_options(self):
        """WorkupForm offers only attending users for 'attending'"""

        form = WorkupForm()

        # find all users able to attest
        attending_users = [u.pk for u in filter(
            lambda u: u.has_perm(Workup.get_sign_perm()), 
            self.users)]

        # c[0] is the pk of each, [1:] indexing required because element 0
        # is the "blank" option.
        attending_options = [c[0] for c in self.form['attending'].field.choices][1:]

        # ensure that options are the same
        assert set(attending_options) == set(attending_users)

        # and that each option is distinct
        assert len(attending_options) == len(attending_users)


    def test_form_other_volunteer_options(self):
        """WorkupForm offers only non-attendings for 'other volunteers'"""

        form = WorkupForm()
        user_pks = [u.pk for u in self.users]
        other_vol_options = [c[0] for c in self.form['other_volunteer'].field.choices]

        # check that any user can be the other volunteer
        assert set(user_pks) == set(other_vol_options)
        assert len(user_pks) == len(other_vol_options)

        # check that error is thrown if one of the other volunteers
        # is the attending
        form_data = wu_dict()
        form_data['attending'] = user_pks[0]
        form_data['other_volunteer'] = [user_pks[0]]
        form = WorkupForm(data=form_data)
        assert len(form['other_volunteer'].errors) > 0

        # and that no error is thrown if they are different
        form_data['other_volunteer'] = [user_pks[1]]
        form = WorkupForm(data=form_data)
        assert len(form['other_volunteer'].errors) == 0

