# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.urls import reverse, resolve
from osler.labs.models import Lab, LabType, ContinuousMeasurement, DiscreteMeasurement, DiscreteResultType, ContinuousMeasurementType, DiscreteMeasurementType
from osler.core.models import (Patient)

from osler.core.tests.test_views import log_in_user, build_user
from osler.users.tests import factories

#from django.contrib.auth import get_user_model
#from django.contrib.auth.models import Permission

from osler.labs import views, forms
from django.utils.timezone import now

from django.shortcuts import get_object_or_404

class TestUrls(TestCase):

    def test_all_labs_list_url(self):
        path = reverse('labs:all-labs', kwargs={'pt_id':1})
        self.assertEqual(resolve(path).view_name, 'labs:all-labs')

    def test_all_labs_url(self):
        path = reverse('labs:all-labs-table', kwargs={'pt_id':1})
        self.assertEqual(resolve(path).view_name, 'labs:all-labs-table')
    def test_lab_detail_url(self):
        path = reverse('labs:lab-detail', kwargs={'pk':1})
        self.assertEqual(resolve(path).view_name, 'labs:lab-detail')

    def test_new_lab_url(self):
        path = reverse('labs:new-lab', kwargs={'pt_id':1})
        self.assertEqual(resolve(path).view_name, 'labs:new-lab')

    def test_new_full_lab_url(self):
        path = reverse('labs:new-full-lab', kwargs={'pt_id':1,
            'lab_type_id':1})
        self.assertEqual(resolve(path).view_name, 'labs:new-full-lab')


class TestModels(TestCase):

    def setUp(self):
        self.ua = LabType.objects.create(name='Urinalysis')

        # Cont measurement with panic levels
        self.ua_pH = ContinuousMeasurementType.objects.create(
            long_name='Urine pH',
            short_name='pH',
            lab_type=self.ua,
            unit='unit',
            panic_upper=10,
            panic_lower=5
            )
        # Cont measurement without panic levels
        self.ua_glucose = ContinuousMeasurementType.objects.create(
            long_name='Urine glucose',
            short_name='glucose',
            lab_type=self.ua
            )
        # Disc measurement
        self.ua_blood = DiscreteMeasurementType.objects.create(
            long_name='Urine blood',
            short_name='blood',
            lab_type=self.ua
            )

        # Disc option, normal
        self.disc_result_neg = DiscreteResultType.objects.create(name='negative', is_panic='F')
        self.disc_result_neg.measurement_type.set([self.ua_blood])


        # Disc option 2, abnormal
        self.disc_result_pos = DiscreteResultType.objects.create(name='positive', is_panic='T')
        self.disc_result_pos.measurement_type.set([self.ua_blood])


        # Disc option 3, abnormal, but doesn't belong to any measurement type
        self.disc_result_trace = DiscreteResultType.objects.create(name='trace', is_panic='T')


    def test_measurement_type_get_ref(self):
        """ Test the get_ref() method for ConitnuousMeasurementType and DiscreteMeasurementType model
        """

        # Continuous measurement type without ref info
        assert self.ua_glucose.get_ref()==''
        self.ua_glucose.unit = 'unit'
        assert self.ua_glucose.get_ref()==''

        # Continuous measurement type with ref info
        self.ua_glucose.panic_lower = 5
        assert self.ua_glucose.get_ref().replace(' ','')=='[5-unit]'
        self.ua_glucose.panic_upper = 10
        assert self.ua_glucose.get_ref().replace(' ','')=='[5-10unit]'

        # Discrete measurement type has no unit
        assert self.ua_blood.get_ref()==''


class TestMeasurementsCreationForm(TestCase):
    """Test the behavior of MeasurementsCreatinoForm which is generated dynamically based on lab_type, and can have complicated behavior when creating and editing.
    """

    fixtures = ['core']

    def setUp(self):
        self.ua = LabType.objects.create(name='Urinalysis')

        # Cont measurement with panic levels
        self.ua_pH = ContinuousMeasurementType.objects.create(
            long_name='Urine pH',
            short_name='pH',
            lab_type=self.ua,
            unit='unit',
            panic_upper=10,
            panic_lower=5
            )
        # Cont measurement without panic levels
        self.ua_glucose = ContinuousMeasurementType.objects.create(
            long_name='Urine glucose',
            short_name='glucose',
            lab_type=self.ua
            )
        # Disc measurement
        self.ua_blood = DiscreteMeasurementType.objects.create(
            long_name='Urine blood',
            short_name='blood',
            lab_type=self.ua
            )

        # Disc option, normal
        self.disc_result_neg = DiscreteResultType.objects.create(name='negative', is_panic='F')
        self.disc_result_neg.measurement_type.set([self.ua_blood])


        # Disc option 2, abnormal
        self.disc_result_pos = DiscreteResultType.objects.create(name='positive', is_panic='T')
        self.disc_result_pos.measurement_type.set([self.ua_blood])


        # Disc option 3, abnormal, but doesn't belong to any measurement type
        self.disc_result_trace = DiscreteResultType.objects.create(name='trace', is_panic='T')

        self.pt = Patient.objects.first()


    def build_form(self, lab_time, pt=None):
        """Util function for generating the form from labtype=ua"""
        if pt==None: pt=self.pt
        form_data = {
            'lab_time': lab_time,
            'patient': pt,
            'pH': 5,
            'glucose': 1,
            'blood': self.disc_result_neg
        }
        return form_data


    def test_submit_form(self):
        """Complete form can be submitted"""
        form_data = self.build_form(lab_time=now())
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)
        assert len(form.errors)==0


    def test_submit_form_incomplete(self):
        """Can't submit incomplete form"""
        form_data = self.build_form(lab_time=now())
        form_data['blood'] = None
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)
        assert len(form.errors)>0


    def test_save_form(self):
        """Create lab & measurement objects when form is saved"""
        form_data = self.build_form(lab_time=now())
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
        form_data = self.build_form(lab_time=now())
        form_data['blood']=None
        form = forms.MeasurementsCreationForm(new_lab_type=self.ua,
            pt=self.pt, data=form_data)
        # Form shouldn't be valid because mt3 value is missing
        if form.is_valid():
            form.save()
        assert not form.is_valid()
        assert not Lab.objects.filter(lab_type=self.ua).exists()
        assert not ContinuousMeasurement.objects.filter(measurement_type=self.ua_pH).exists()
        assert not ContinuousMeasurement.objects.filter(measurement_type=self.ua_glucose).exists()
        assert not DiscreteMeasurement.objects.filter(measurement_type=self.ua_blood).exists()


    def test_edit_form(self):
        form_data = self.build_form(lab_time=now())
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

    fixtures = ['core']

    def setUp(self):
        self.ua = LabType.objects.create(name='Urinalysis')

        # Cont measurement with panic levels
        self.ua_pH = ContinuousMeasurementType.objects.create(
            long_name='Urine pH',
            short_name='pH',
            lab_type=self.ua,
            unit='unit',
            panic_upper=10,
            panic_lower=5
            )
        # Cont measurement without panic levels
        self.ua_glucose = ContinuousMeasurementType.objects.create(
            long_name='Urine glucose',
            short_name='glucose',
            lab_type=self.ua
            )
        # Disc measurement
        self.ua_blood = DiscreteMeasurementType.objects.create(
            long_name='Urine blood',
            short_name='blood',
            lab_type=self.ua
            )

        # Disc option, normal
        self.disc_result_neg = DiscreteResultType.objects.create(name='negative', is_panic='F')
        self.disc_result_neg.measurement_type.set([self.ua_blood])

        self.pt = Patient.objects.first()

        form_data = {
            'lab_time': now(),
            'patient': self.pt,
            'pH': 5,
            'glucose': 1,
            'blood': self.disc_result_neg
        }

        form = forms.MeasurementsCreationForm(new_lab_type=self.ua, pt=self.pt, data=form_data)
        if form.is_valid():
            form.save()


    def test_lab_list_view(self):
        """Any user able to view all lab list view"""
        log_in_user(self.client, build_user())
        url = reverse('labs:all-labs', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200


    def test_lab_table_view(self):
        """Any user able to view all lab table view"""
        log_in_user(self.client, build_user())
        url = reverse('labs:all-labs-table', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200


    def test_lab_detail_view(self):
        """Any user able to view all lab table view"""
        log_in_user(self.client, build_user())

        lab = Lab.objects.first()
        url = reverse('labs:lab-detail', kwargs={'pk':lab.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200

        fake_pk = 0
        assert not Lab.objects.filter(pk=fake_pk).exists()
        url = reverse('labs:lab-detail', kwargs={'pk':fake_pk})
        response = self.client.get(url)
        print(response)
        assert response.status_code == 404


    def test_lab_add_view_with_perm(self):
        """User with lab permissions is able to add lab"""
        log_in_user(self.client, build_user([factories.CaseManagerGroupFactory]))

        url = reverse('labs:new-lab', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200


    def test_lab_add_view_no_perm(self):
        """User without lab permissions can't add lab"""
        log_in_user(self.client, build_user([factories.NoPermGroupFactory]))

        url = reverse('labs:new-lab', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 403


    def test_lab_edit_view_with_perm(self):
        """User with lab permissions is able to edit lab"""
        log_in_user(self.client, build_user([factories.CaseManagerGroupFactory]))

        lab = Lab.objects.first()
        url = reverse('labs:lab-edit', kwargs={'pk':lab.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 200


    def test_lab_edit_view_no_perm(self):
        """User without lab permissions can't edit lab"""
        log_in_user(self.client, build_user([factories.NoPermGroupFactory]))

        lab = Lab.objects.first()
        url = reverse('labs:lab-edit', kwargs={'pk':lab.id})
        response = self.client.get(url, follow=True)
        assert response.status_code == 403