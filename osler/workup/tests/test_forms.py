from __future__ import division
from __future__ import unicode_literals
from builtins import str
from builtins import range
from past.utils import old_div
import decimal

from django.test import TestCase
from django.forms.models import model_to_dict

from osler.core.models import Gender

from osler.workup.models import DiagnosisType, Workup
from osler.workup.forms import WorkupForm

from osler.workup.tests.tests import note_dict
from osler.workup.tests import factories as workup_factories

from osler.core.tests.test_views import build_user
import osler.users.tests.factories as user_factories
import osler.core.tests.factories as core_factories

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

    def setUp(self):
        DiagnosisType.objects.create(name='Cardiovascular')

        wu = workup_factories.WorkupFactory()
        self.wu = wu
        self.pt = wu.patient

    def test_vitals_no_units_error(self):
        """If vitals measurement w/o units, raise error"""

        wu_data = model_to_dict(self.wu)
        
        wu_data['t'] = 98.6
        wu_data['height'] = 100
        wu_data['weight'] = 180

        form = WorkupForm(pt = self.pt, data = wu_data)

        for field in ['t', 'height', 'weight']:
            self.assertFalse(form.is_valid(), msg = 'Failed to raise error if only %s specified' % field) 
            self.assertNotEqual(len(form[field].errors),0)

    def test_vitals_no_value_no_units_ok(self):
        """Units are required only when vitals are provided."""

        wu_data = model_to_dict(self.wu)

        del wu_data['height']
        del wu_data['weight']
        del wu_data['t']

        form = WorkupForm(pt = self.pt, data = wu_data)
        self.assertTrue(form.is_valid(), msg = form.errors)

    def test_note_temp_conversion(self):

        wu_data = model_to_dict(self.wu) 
       
        wu_data['temperature_units'] = 'C'
        wu_data['t'] = 37

        wu_data['height_units'] = 'cm'
        wu_data['height'] = 180
        
        wu_data['weight_units'] = 'kg'
        wu_data['weight'] = 180

        form = WorkupForm(pt=self.pt,data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            form.cleaned_data['t'],
            wu_data['t'])

        # temperatures given centigrade should be converted
        wu_data['temperature_units'] = 'F'
        wu_data['t'] = 98
        form = WorkupForm(pt=self.pt,data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            round((wu_data['t'] - 32) * decimal.Decimal(5 / 9.0)),
            round(decimal.Decimal(form.cleaned_data['t'])))

    def test_note_height_conversion(self):

        wu_data = model_to_dict(self.wu)
        # heights with cm should be the same
        wu_data['height_units'] = 'cm'
        wu_data['height'] = 180
        
        wu_data['weight_units'] = 'kg'
        wu_data['weight'] = 180
        wu_data['temperature'] = 98
        wu_data['temperature_units'] = 'F'

        form = WorkupForm(pt=self.pt,data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            form.cleaned_data['height'],
            wu_data['height'])

        # heights given inches should be converted
        wu_data['height_units'] = 'in'
        wu_data['height'] = 71

        form = WorkupForm(pt=self.pt,data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            form.cleaned_data['height'],
            round(wu_data['height'] * decimal.Decimal(2.54), 0))

    def test_note_weight_conversion(self):

        wu_data = model_to_dict(self.wu)

        # weights with kilograms should be the same
        wu_data['weight_units'] = 'kg'
        wu_data['weight'] = 81

         #adding this in but doesn't seem right:
        wu_data['height_units'] = 'cm'
        wu_data['height'] = 180
        wu_data['temperature'] = 98
        wu_data['temperature_units'] = 'F'

        form = WorkupForm(pt=self.pt,data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            form.cleaned_data['weight'],
            wu_data['weight'])

        # weights given lbs should be converted
        wu_data['weight_units'] = 'lbs'

        form = WorkupForm(pt=self.pt,data=wu_data)

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(
            round(form.cleaned_data['weight']),
            round(old_div(wu_data['weight'], decimal.Decimal(2.2))))


class TestWorkupFormValidators(TestCase):


    fixtures = ['workup', 'core']

    def setUp(self):
        self.wu = workup_factories.WorkupFactory()
        self.valid_wu_dict = model_to_dict(self.wu)
        self.pt = self.wu.patient


    def test_blood_pressure_together(self):
        """Systolic and diastolic bp must be specified together."""

        form_data = self.valid_wu_dict.copy()
        del form_data['bp_sys']

        form = WorkupForm(pt=self.pt,data=form_data)
        self.assertFalse(form.is_valid())

        form_data = self.valid_wu_dict.copy()
        del form_data['bp_dia']

        form = WorkupForm(pt=self.pt,data=form_data)
        self.assertFalse(form.is_valid())

    def test_blood_pressure(self):

        form_data = self.valid_wu_dict
        form = WorkupForm(pt=self.pt,data=form_data)

        self.assertEqual(len(form['bp_sys'].errors), 0)
        self.assertEqual(len(form['bp_dia'].errors), 0)

        form_data['bp_sys'] = '800'

        form = WorkupForm(pt=self.pt,data=form_data)
        self.assertNotEqual(len(form['bp_sys'].errors), 0)

        form_data['bp_sys'] = '120'
        form_data['bp_dia'] = '30'

        form = WorkupForm(pt=self.pt,data=form_data)
        self.assertNotEqual(len(form['bp_dia'].errors), 0)

        # the systolic < diastolic error is a bp_sys error not bp_dia
        form_data['bp_dia'] = '130'
        form = WorkupForm(pt=self.pt,data=form_data)
        self.assertNotEqual(len(form['bp_sys'].errors), 0)

    def test_missing_voucher_amount(self):

        
        form_data = self.valid_wu_dict
        del form_data['voucher_amount']
        del form_data['imaging_voucher_amount']
        form_data['got_voucher'] = True
        form_data['got_imaging_voucher'] = True

        form = WorkupForm(pt=self.pt,data=form_data)

        self.assertNotEqual(len(form['voucher_amount'].errors), 0)
        self.assertNotEqual(len(form['patient_pays'].errors), 0)

        form_data['voucher_amount'] = '40'
        form_data['patient_pays'] = '40'

        form = WorkupForm(pt=self.pt,data=form_data)
        self.assertEqual(len(form['voucher_amount'].errors), 0)
        self.assertEqual(len(form['patient_pays'].errors), 0)

        self.assertNotEqual(len(form['imaging_voucher_amount'].errors), 0)
        self.assertNotEqual(len(form['patient_pays_imaging'].errors), 0)

        form_data['imaging_voucher_amount'] = '40'
        form_data['patient_pays_imaging'] = '40'

        form = WorkupForm(pt=self.pt,data=form_data)
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
        self.pt = core_factories.PatientFactory()
        

    def test_form_attending_options(self):
        """WorkupForm offers only attending users for 'attending'"""

        form = WorkupForm(pt=self.pt)

        # find all users able to attest
        attending_users = [u for u in filter(
            lambda u: u.has_perm(Workup.get_sign_perm()), 
            self.users)]

        attending_options = form['attending'].field.queryset

        # ensure that options are the same
        assert set(attending_options) == set(attending_users)

        # and that each option is distinct
        assert len(attending_options) == len(attending_users)


    def test_form_other_volunteer_options(self):
        """WorkupForm offers only non-attendings for 'other volunteers'"""

        
        form = WorkupForm(pt=self.pt)
        
        user_pks = [u for u in self.users]
        other_vol_options = form['other_volunteer'].field.queryset

        # check that any user can be the other volunteer
        assert set(user_pks) == set(other_vol_options)
        assert len(user_pks) == len(other_vol_options)

        # check that error is thrown if one of the other volunteers
        # is the attending
        attending = build_user([user_factories.AttendingGroupFactory])
        non_attending = build_user()
        DiagnosisType.objects.create(name='Cardiovascular')
        form_data = model_to_dict(workup_factories.WorkupFactory())

        pt = form_data['patient']
        form_data['attending'] = attending
        form_data['other_volunteer'] = [non_attending, attending]
        form = WorkupForm(pt=pt,data=form_data)
        assert form['other_volunteer'].errors

        # and that no error is thrown if they are different
        form_data['other_volunteer'] = [non_attending]
        form = WorkupForm(pt=pt,data=form_data)
        assert not form['other_volunteer'].errors

