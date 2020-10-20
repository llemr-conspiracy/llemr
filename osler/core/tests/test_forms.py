import factory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from osler.core.models import ActionInstruction
from osler.core import forms

from osler.core.tests import factories
from osler.users.tests import factories as user_factories

User = get_user_model()


class TestActionItemCreateForms(TestCase):
    '''Tests for form used to create new Action Items'''

    def setUp(self):
        self.user = user_factories.UserFactory()
        self.ai_data = factory.build(
            dict, FACTORY_CLASS=factories.ActionItemFactory)

    def test_instruction_inactive(self):
        """Action Item Form only shows active instructions as options."""

        PCP_followup = ActionInstruction.objects.create(
            instruction='PCP Followup', active=False)
        Lab_Followup = ActionInstruction.objects.create(
            instruction='Lab Followup', active=True)

        ai_qs = ActionInstruction.objects.filter(
            active=True)

        form = forms.ActionItemForm(data=self.ai_data)

        form_qs = form['instruction'].field.queryset

        assert set(ai_qs) == set(form_qs)
        assert len(ai_qs) == len(form_qs)

        # Accept active Action Instructions
        self.ai_data['instruction'] = Lab_Followup.pk
        form = forms.ActionItemForm(data=self.ai_data)
        assert len(form['instruction'].errors) == 0

        # Reject inactive Action Instructions
        self.ai_data['instruction'] = PCP_followup.pk
        form = forms.ActionItemForm(data=self.ai_data)
        assert len(form['instruction'].errors) != 0


class TestPatientCreateForms(TestCase):
    '''Tests for the form used to create new Patients.'''

    def setUp(self):

        self.valid_pt_dict = factory.build(
            dict, FACTORY_CLASS=factories.PatientFactory)

    def test_form_casemanager_options(self):
        """PatientForm only offers valid case managers as options.
        """

        pvds = user_factories.UserFactory.create_batch(3)

        casemanager = user_factories.CaseManagerGroupFactory()
        not_casemanager = user_factories.VolunteerGroupFactory()

        assert Permission.objects.filter(
            codename='case_manage_Patient').count() == 1

        pvds[0].groups.add(not_casemanager)
        pvds[1].groups.add(casemanager)
        pvds[2].groups.add(not_casemanager, casemanager)
        [p.save() for p in pvds]

        cm_qs = User.objects.filter(
            groups__in=[casemanager])

        form = forms.PatientForm()

        form_qs = form['case_managers'].field.queryset

        # avoid strange behavior with assertQuerysetEqual
        assert set(cm_qs) == set(form_qs)
        assert len(cm_qs) == len(form_qs)


        # Make sure we reject non-case manager providers

        form = forms.PatientForm()
        form_data = self.valid_pt_dict.copy()
        form_data['case_managers'] = [pvds[0]]
        form = forms.PatientForm(data=form_data)
        assert len(form['case_managers'].errors) != 0

        form_data = self.valid_pt_dict.copy()
        form_data['case_managers'] = [pvds[1].pk]
        form = forms.PatientForm(data=form_data)
        assert len(form['case_managers'].errors) == 0

        # Make sure we accept case manager providers
        form_data = self.valid_pt_dict.copy()
        form_data['case_managers'] = [pvds[2].pk]
        form = forms.PatientForm(data=form_data)
        assert len(form['case_managers'].errors) == 0

    def test_missing_alt_phone(self):
        '''Missing the alternative phone w/o alt phone owner should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1_owner'] = "Jamal"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)

        # and expect an error to be on the empty altphone field
        self.assertNotEqual(len(form['alternate_phone_1'].errors), 0)

    def test_missing_alt_phone_owner(self):
        '''Missing the alt phone owner w/o alt phone should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1'] = "4258612322"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)
        # we expect errors on the empty alternate_phone_1_owner field
        self.assertNotEqual(len(form['alternate_phone_1_owner'].errors), 0)
