# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.urls import reverse, resolve
from django.shortcuts import redirect
from osler.labs.models import Lab, LabType, ContinuousMeasurement, DiscreteMeasurement, DiscreteResultType, ContinuousMeasurementType, DiscreteMeasurementType
from osler.core.models import (Patient)

from osler.core.tests.test_views import log_in_user, build_user
from osler.core.tests import factories as core_factories
from osler.users.tests import factories as user_factories
from osler.labs.tests import factories

from osler.labs import views, forms
from django.utils.timezone import now

from django.shortcuts import get_object_or_404


class TestModels(TestCase):

    def setUp(self):
        self.ua = factories.LabTypeFactory(name='Urinalysis')

        # Cont measurement without panic levels
        self.ua_glucose = factories.ContinuousMeasurementTypeFactory(
            long_name='Urine glucose',
            short_name='glucose',
            lab_type=self.ua,
            unit=None,
            panic_lower=None,
            panic_upper=None
            )
        # Disc measurement
        self.ua_blood = factories.DiscreteMeasurementTypeFactory(
            long_name='Urine blood',
            short_name='blood',
            lab_type=self.ua
            )
      
        # Disc option 1, normal
        self.disc_result_neg = factories.DiscreteResultTypeFactory(name='neg', is_panic='F')
        self.disc_result_neg.measurement_type.set([self.ua_blood])
        # Disc option 2, abnormal
        self.disc_result_pos = factories.DiscreteResultTypeFactory(name='pos', is_panic='T')
        self.disc_result_pos.measurement_type.set([self.ua_blood])

        self.pt = core_factories.PatientFactory()
        self.lab = factories.LabFactory(patient=self.pt, lab_type=self.ua)


    def test_measurement_type_get_ref(self):
        """ Test the get_ref() method for ConitnuousMeasurementType and DiscreteMeasurementType model
        """

        # Continuous measurement type without ref info
        assert self.ua_glucose.get_ref()==''
        self.ua_glucose.unit = 'unit'
        assert self.ua_glucose.get_ref()==''

        # Continuous measurement type with ref info
        self.ua_glucose.panic_lower = 5
        assert self.ua_glucose.get_ref().replace(' ','')=='[5.0-unit]'
        self.ua_glucose.panic_upper = 10
        assert self.ua_glucose.get_ref().replace(' ','')=='[5.0-10.0unit]'

        # Discrete measurement type has no unit
        assert self.ua_blood.get_ref()==''


    def test_measurement_type_panic_discrete(self):
        """ Test the panic() and panic_low() method for DiscreteMeasurement model
        """
        # Normal value 
        lab_ua_blood_neg = factories.DiscreteMeasurementFactory(measurement_type=self.ua_blood, lab=self.lab, value=self.disc_result_neg)

        assert not lab_ua_blood_neg.panic()
        assert not lab_ua_blood_neg.panic_low()

        # Abnormal value 
        lab_ua_blood_pos = factories.DiscreteMeasurementFactory(measurement_type=self.ua_blood, lab=self.lab, value=self.disc_result_pos)

        assert lab_ua_blood_pos.panic()
        assert not lab_ua_blood_pos.panic_low()


    def test_measurement_type_panic_continuous(self):
        """ Test the panic() and panic_low() method for ContinuouseMeasurement model
        """
        lab_ua_glucose = factories.ContinuousMeasurementFactory(measurement_type=self.ua_glucose, lab=self.lab, value=5)

        # No reference don't panic
        assert not lab_ua_glucose.panic()
        assert not lab_ua_glucose.panic_low()

        # Test upper reference, normal value
        self.ua_glucose.panic_upper = 10
        assert not lab_ua_glucose.panic()
        assert not lab_ua_glucose.panic_low()

        # Test upper reference, abnormal value
        self.ua_glucose.panic_upper = 2
        assert lab_ua_glucose.panic()
        assert not lab_ua_glucose.panic_low()

        # Test lower reference, normal value
        self.ua_glucose.panic_upper = None
        self.ua_glucose.panic_lower = 2
        assert not lab_ua_glucose.panic()
        assert not lab_ua_glucose.panic_low()

        # Test lower reference, abnormal value
        self.ua_glucose.panic_lower = 10
        assert lab_ua_glucose.panic()
        assert lab_ua_glucose.panic_low()


class TestMeasurementsCreationForm(TestCase):
    """Test the behavior of MeasurementsCreatinoForm which is generated dynamically based on lab_type, and can have complicated behavior when creating and editing.
    """

    def setUp(self):
        self.ua = factories.LabTypeFactory(name='Urinalysis')

        self.ua_pH = factories.ContinuousMeasurementTypeFactory(
            long_name='Urine pH',
            short_name='pH',
            lab_type=self.ua
            )

        self.ua_glucose = factories.ContinuousMeasurementTypeFactory(
            long_name='Urine glucose',
            short_name='glucose',
            lab_type=self.ua
            )
        # Disc measurement
        self.ua_blood = factories.DiscreteMeasurementTypeFactory(
            long_name='Urine blood',
            short_name='blood',
            lab_type=self.ua
            )

        # Disc option 1
        self.disc_result_neg = factories.DiscreteResultTypeFactory(name='neg')
        self.disc_result_neg.measurement_type.set([self.ua_blood])


        # Disc option 2
        self.disc_result_pos = factories.DiscreteResultTypeFactory(name='pos')
        self.disc_result_pos.measurement_type.set([self.ua_blood])

        self.pt = core_factories.PatientFactory()
        self.encounter = core_factories.EncounterFactory(
            patient=self.pt,
            status=core_factories.EncounterStatusFactory(name="Active",is_active=True))

        self.form_data = {
            'lab_time': now(),
            'patient': self.pt,
            'pH': 5,
            'glucose': 1,
            'blood': self.disc_result_neg,
            'encounter': self.encounter
        }


    def test_submit_form(self):
        """Complete form can be submitted"""
        form_data = self.form_data.copy()
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)
        assert len(form.errors)==0


    def test_submit_form_incomplete(self):
        """Can't submit incomplete form"""
        form_data = self.form_data.copy()
        form_data['blood'] = None
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)
        assert len(form.errors)>0


    def test_save_form(self):
        """Create lab & measurement objects when form is saved"""
        form_data = self.form_data.copy()
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)

        # Before submitting forms, objects don't exist
        assert not Lab.objects.filter(lab_type=self.ua).exists()
        assert not ContinuousMeasurement.objects.filter(measurement_type=self.ua_pH).exists()
        assert not ContinuousMeasurement.objects.filter(measurement_type=self.ua_glucose).exists()
        assert not DiscreteMeasurement.objects.filter(measurement_type=self.ua_blood).exists()

        if form.is_valid():
            form.save()
            assert Lab.objects.filter(lab_type=self.ua).exists(),True
            lab = Lab.objects.get(lab_type=self.ua)
            assert ContinuousMeasurement.objects.get(measurement_type=self.ua_pH, lab=lab).value == form_data['pH']
            assert ContinuousMeasurement.objects.get(measurement_type=self.ua_glucose, lab=lab).value == form_data['glucose']
            assert DiscreteMeasurement.objects.get(measurement_type=self.ua_blood, lab=lab).value == form_data['blood']
        else:
            self.fail('Measurement Creation Form not valid')


    def test_save_form_incomplete(self):
        """Don't create any lab & measurement objects when the form is incomplete (even when the info for some objects are complete)"""
        form_data = self.form_data.copy()
        form_data['blood']=None
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)
        # Form shouldn't be valid because one measurement value is missing
        if form.is_valid():
            form.save()
        assert not form.is_valid()
        assert not Lab.objects.filter(lab_type=self.ua).exists()
        assert not ContinuousMeasurement.objects.filter(measurement_type=self.ua_pH).exists()
        assert not ContinuousMeasurement.objects.filter(measurement_type=self.ua_glucose).exists()
        assert not DiscreteMeasurement.objects.filter(measurement_type=self.ua_blood).exists()


    def test_edit_form(self):
        form_data = self.form_data.copy()
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)
        new_pH_value = 100
        if form.is_valid():
            form.save()
        form_data['pH']= new_pH_value
        assert form_data['pH']==new_pH_value

        lab = Lab.objects.get(lab_type=self.ua)

        edited_form = forms.MeasurementsCreationForm(new_lab_type=self.ua, pt=self.pt, lab_pk=lab.id, data=form_data)
        if edited_form.is_valid():
            edited_form.save(lab_pk=lab.id)
        else:
            self.fail('Edited form not valid')
        assert len(Lab.objects.all()) == 1
        assert len(ContinuousMeasurement.objects.filter(measurement_type=self.ua_pH)) == 1

        new_pH = ContinuousMeasurement.objects.get(measurement_type=self.ua_pH)
        assert new_pH.value, new_pH_value


class TestLabView(TestCase):
    """
    Test all views in lab
    """

    def setUp(self):
        self.ua = factories.LabTypeFactory(name='Urinalysis')
        self.ua_pH = factories.ContinuousMeasurementTypeFactory(
            long_name='Urine pH',
            short_name='pH',
            lab_type=self.ua
            )
        self.ua_glucose = factories.ContinuousMeasurementTypeFactory(
            long_name='Urine glucose',
            short_name='glucose',
            lab_type=self.ua
            )
        self.ua_blood = factories.DiscreteMeasurementTypeFactory(
            long_name='Urine blood',
            short_name='blood',
            lab_type=self.ua
            )

        self.disc_result_neg = factories.DiscreteResultTypeFactory(name='neg')
        self.disc_result_neg.measurement_type.set([self.ua_blood])

        self.pt = core_factories.PatientFactory()
        self.lab = factories.LabFactory(patient=self.pt, lab_type=self.ua)

        lab_ua_pH = factories.ContinuousMeasurementFactory(measurement_type=self.ua_pH, lab=self.lab)
        lab_ua_glucose = factories.ContinuousMeasurementFactory(measurement_type=self.ua_glucose, lab=self.lab)
        lab_ua_blood = factories.DiscreteMeasurementFactory(measurement_type=self.ua_blood, lab=self.lab)

        log_in_user(self.client, build_user())

        self.submitted_form_step1 = {
            "lab_type": self.ua.id
        }

        self.submitted_form_step2 = {
            'lab_time': now().strftime("%Y-%m-%d %H:%M:%S"),
            'pH': '5',
            'glucose': '1',
            'blood': self.disc_result_neg.name,
            'encounter': self.lab.encounter.id
        }


    def test_lab_list_view(self):
        """Any user able to view all lab list view"""
        url = reverse('labs:all-labs', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200


    def test_lab_table_view(self):
        """Any user able to view all lab table view"""
        url = reverse('labs:all-labs-table', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200


    def test_lab_detail_view(self):
        """Any user able to view all lab table view"""
        lab = self.lab
        url = reverse('labs:lab-detail', kwargs={'pk':lab.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200

        fake_pk = 0
        assert not Lab.objects.filter(pk=fake_pk).exists()
        url = reverse('labs:lab-detail', kwargs={'pk':fake_pk})
        response = self.client.get(url)
        assert response.status_code == 404


    def test_lab_add_view_with_perm(self):
        """User with lab permissions is able to add lab"""
        log_in_user(self.client, build_user([user_factories.CaseManagerGroupFactory]))

        assert ContinuousMeasurement.objects.count() == 2
        assert DiscreteMeasurement.objects.count() == 1
        assert Lab.objects.count() == 1

        url = reverse('labs:new-lab', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url)
        assert response.status_code == 200

        response = self.client.post(url, self.submitted_form_step1)
        assert response.status_code == 302

        # Successfully redirect to step 2 view
        url = reverse('labs:new-full-lab', kwargs={'pt_id':self.pt.id, 'lab_type_id':self.ua.id})
        assert response.url == url

        response = self.client.post(url, self.submitted_form_step2)
        assert response.status_code == 302

        # Successfully added lab and measurement objects
        assert ContinuousMeasurement.objects.count() == 4
        assert DiscreteMeasurement.objects.count() == 2
        assert Lab.objects.count() == 2

        # Successfully redirect back to table view
        url = reverse("labs:all-labs-table", kwargs={'pt_id':self.pt.id})
        assert response.url == url


    def test_lab_add_view_no_perm(self):
        """User without lab permissions can't add lab"""
        log_in_user(self.client, build_user([user_factories.NoPermGroupFactory]))

        url = reverse('labs:new-lab', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 403


    def test_lab_edit_view_with_perm(self):
        """User with lab permissions is able to edit lab"""
        log_in_user(self.client, build_user([user_factories.CaseManagerGroupFactory]))

        lab = self.lab
        assert Lab.objects.count() == 1

        url = reverse('labs:lab-edit', kwargs={'pk':lab.id})
        response = self.client.get(url)
        response = self.client.post(url, self.submitted_form_step2)
        assert response.status_code == 302

        # Successfully redirect back to detail view
        url = reverse("labs:lab-detail", kwargs={'pk':lab.id})
        assert response.url == url

        # Successfully edited measurement values without creating a new lab object
        assert Lab.objects.count() == 1
        assert int(ContinuousMeasurement.objects.filter(measurement_type=self.ua_pH).last().value) == int(self.submitted_form_step2['pH'])


    def test_lab_edit_view_no_perm(self):
        """User without lab permissions can't edit lab"""
        log_in_user(self.client, build_user([user_factories.NoPermGroupFactory]))

        lab = self.lab
        url = reverse('labs:lab-edit', kwargs={'pk':lab.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 403