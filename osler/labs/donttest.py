# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.urls import reverse, resolve
from osler.labs.models import *
from osler.core.models import (Patient, Gender)

from osler.core.tests.test_views import log_in_user, build_user

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

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

    def test_lab_delete_url(self):
        path = reverse('labs:lab-delete', kwargs={'pk':1})
        self.assertEqual(resolve(path).view_name, 'labs:lab-delete')



class TestModels(TestCase):

    def setUp(self):
        lab_type1 = LabType.objects.create(name='testlabtype')

        # Cont measurement with panic levels
        measure_type1 = MeasurementType.objects.create(
            long_name='testmeasurementtype',
            short_name='testmt',
            lab_type=lab_type1,
            unit='unit',
            panic_upper=10,
            panic_lower=5,
            value_type='Continuous'
            )
        # Cont measurement without panic levels
        measure_type2nopanic = MeasurementType.objects.create(
            long_name='testmeasurementtype2',
            short_name='testmt2',
            lab_type=lab_type1,
            value_type='Continuous'
            )
        # Disc measurement
        measure_type3dist = MeasurementType.objects.create(
            long_name='testmeasurementtype3',
            short_name='testmt3',
            lab_type=lab_type1,
            value_type='Discrete'
            )

        # Disc option 1, normal
        option1 = DiscreteResultType(
            name='option1',
            is_panic='F')
        option1.save()
        option1.measurement_type.set([measure_type3dist])
        option1.save()

        # Disc option 2, abnormal
        option2 = DiscreteResultType(
            name='option2',
            is_panic='T')
        option2.save()
        option2.measurement_type.set([measure_type3dist])
        option2.save()

        # Disc option 3, abnormal, but doesn't belong to any measurement type
        option3 = DiscreteResultType(
            name='option3',
            is_panic='T')
        option3.save()


    def test_measurement_type_panic(self):
        """ Test the panic(value) method for MeasurementType model
        """
        measure_type1 = MeasurementType.objects.get(short_name='testmt')
        measure_type2 = MeasurementType.objects.get(short_name='testmt2')
        measure_type3 = MeasurementType.objects.get(short_name='testmt3')
        option1 = DiscreteResultType.objects.get(name='option1')
        option2 = DiscreteResultType.objects.get(name='option2')
        option3 = DiscreteResultType.objects.get(name='option3')

        # Value lower than lower reference
        self.assertEqual(measure_type1.panic(3),True)

        # Value higher than higher reference
        self.assertEqual(measure_type1.panic(15),True)

        # No panic if no value provided
        self.assertEqual(measure_type2.panic(3),False)
        self.assertEqual(measure_type2.panic(1000),False)

        # Panic if only one side of ref is provided
        measure_type2.panic_lower=10
        measure_type2.save()
        self.assertEqual(measure_type2.panic(3),True)
        self.assertEqual(measure_type2.panic(10000),False)
        measure_type2.panic_lower=None
        measure_type2.save()

        # Panic works after editing
        self.assertEqual(measure_type2.panic(3),False)

        # Panic works in discrete types too
        self.assertEqual(measure_type3.panic(option1),False)
        self.assertEqual(measure_type3.panic(option2),True)

        # Don't panic if an abnormal value for another measurement is compared here
        self.assertEqual(measure_type3.panic(option3),False)


    def test_measurement_type_get_ref(self):
        """ Test the get_ref() method for MeasurementType model
        """

        # Continuous measurement type without ref info
        measure_type2 = MeasurementType.objects.get(short_name='testmt2')
        self.assertEqual(measure_type2.get_ref(),'')
        measure_type2.unit = 'unit'
        self.assertEqual(measure_type2.get_ref(),'')

        # Continuous measurement type with ref info
        measure_type2.panic_lower = 5
        self.assertEqual(measure_type2.get_ref().replace(' ',''),'[5-unit]')
        measure_type2.panic_upper = 10
        self.assertEqual(measure_type2.get_ref().replace(' ',''),'[5-10unit]')

        # Discrete measurement type has no unit
        measure_type3 = MeasurementType.objects.get(short_name='testmt3')
        self.assertEqual(measure_type3.get_ref(),'')
        

class TestMeasurementsCreationForm(TestCase):
    """Test the behavior of MeasurementsCreatinoForm which is generated dynamically based on lab_type, and can have complicated behavior when creating and editing.
    """

    fixtures = ['core']

    def setUp(self):
        TestModels().setUp()
        self.pt = Patient.objects.first()

    """Util function for generating the form from labtype"""
    def build_form(self, lab_type, lab_time, pt=None):
        if pt==None: pt=self.pt
        form_data = {
            'lab_time': lab_time,
            'lab_type':lab_type,
            'patient': pt,
            'testmt': 1,
            'testmt2': 2,
            'testmt3': DiscreteResultType.objects.get(name='option1')
        }
        return form_data

    # Successful build
    def test_build_form(self):
        lt1 = LabType.objects.get(name='testlabtype')
        form_data = self.build_form(
            lab_type=lt1,
            lab_time=now()
            )
        form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, data=form_data)
        self.assertEqual(len(form.errors), 0)

    # Can't submit incomplete form
    def test_build_form_incomplete(self):
        lt1 = LabType.objects.get(name='testlabtype')
        form_data = self.build_form(
            lab_type=lt1,
            lab_time=now()
            )
        form_data['testmt3'] = None
        form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, data=form_data)
        self.assertEqual(len(form.errors), 1)

    # Create lab & measurement objects when form is saved
    def test_save_form(self):
        lt1 = LabType.objects.get(name='testlabtype')
        mt1 = MeasurementType.objects.get(short_name='testmt')
        mt2 = MeasurementType.objects.get(short_name='testmt2')
        mt3 = MeasurementType.objects.get(short_name='testmt3')
        form_data = self.build_form(
            lab_type=lt1,
            lab_time=now()
            )
        form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, data=form_data)
        self.assertEqual(Lab.objects.filter(lab_type=lt1).exists(),False)
        self.assertEqual(ContinuousMeasurement.objects.filter(measurement_type=mt1).exists(),False)
        self.assertEqual(ContinuousMeasurement.objects.filter(measurement_type=mt2).exists(),False)
        self.assertEqual(DiscreteMeasurement.objects.filter(measurement_type=mt3).exists(),False)
        if form.is_valid():
            form.save()
            self.assertEqual(Lab.objects.filter(lab_type=lt1).exists(),True)
            lab = Lab.objects.get(lab_type=lt1)
            self.assertEqual(ContinuousMeasurement.objects.get(measurement_type=mt1, lab=lab).value, form_data['testmt'])
            self.assertEqual(ContinuousMeasurement.objects.get(measurement_type=mt2, lab=lab).value, form_data['testmt2'])
            self.assertEqual(DiscreteMeasurement.objects.get(measurement_type=mt3, lab=lab).value, form_data['testmt3'])
        else:
            self.fail('Measurement Creation Form not valid')


    # Don't create any lab & measurement objects when the form is incomplete (even when the info for some objects are complete)
    def test_save_form_incomplete(self):
        lt1 = LabType.objects.get(name='testlabtype')
        mt1 = MeasurementType.objects.get(short_name='testmt')
        mt2 = MeasurementType.objects.get(short_name='testmt2')
        mt3 = MeasurementType.objects.get(short_name='testmt3')
        form_data = self.build_form(
            lab_type=lt1,
            lab_time=now()
            )
        form_data['testmt3']=None
        form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, data=form_data)
        # Form shouldn't be valid because mt3 value is missing
        if form.is_valid():
            form.save()
        self.assertEqual(Lab.objects.filter(lab_type=lt1).exists(),False)
        self.assertEqual(ContinuousMeasurement.objects.filter(measurement_type=mt1).exists(),False)
        self.assertEqual(ContinuousMeasurement.objects.filter(measurement_type=mt2).exists(),False)
        self.assertEqual(DiscreteMeasurement.objects.filter(measurement_type=mt3).exists(),False)


    def test_edit_form(self):
        lt1 = LabType.objects.get(name='testlabtype')
        mt1 = MeasurementType.objects.get(short_name='testmt')
        lab_time = now()
        new_mt1_value = 100
        form_data = self.build_form(
            lab_type=lt1,
            lab_time=lab_time
            )
        form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, data=form_data)
        if form.is_valid():
            form.save()
        form_data['testmt']= new_mt1_value
        new_lab = Lab.objects.get(lab_type=lt1)
        new_m1 = ContinuousMeasurement.objects.get(measurement_type=mt1, lab=new_lab)

        self.assertEqual(form_data['testmt'], new_mt1_value)
        edited_form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, lab_pk=new_lab.id, data=form_data)
        if edited_form.is_valid():
            edited_form.save(lab_pk=new_lab.id)
        else:
            self.fail('Edited form not valid')
        self.assertEqual(len(Lab.objects.all()), 1)
        self.assertEqual(len(ContinuousMeasurement.objects.filter(measurement_type=mt1)), 1)

        new_m1_edit = ContinuousMeasurement.objects.get(pk=new_m1.id)
        self.assertEqual(new_m1_edit.value, new_mt1_value)


    def test_delete_form(self):
        self.assertEqual(len(Lab.objects.all()),0)
        self.assertEqual(len(ContinuousMeasurement.objects.all()),0)
        self.assertEqual(len(DiscreteMeasurement.objects.all()),0)

        lt1 = LabType.objects.get(name='testlabtype')
        form_data = self.build_form(
            lab_type=lt1,
            lab_time=now()
            )
        form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, data=form_data)
        if form.is_valid():
            form.save()
            self.assertEqual(Lab.objects.filter(lab_type=lt1).exists(),True)
            lab = Lab.objects.get(lab_type=lt1)
        else:
            self.fail('Invalid form')

        self.assertEqual(len(Lab.objects.all()),1)
        self.assertEqual(len(ContinuousMeasurement.objects.all()),2)
        self.assertEqual(len(DiscreteMeasurement.objects.all()),1)

        lab.delete()

        self.assertEqual(len(Lab.objects.all()),0)
        self.assertEqual(len(ContinuousMeasurement.objects.all()),0)
        self.assertEqual(len(DiscreteMeasurement.objects.all()),0)



class TestLabView(TestCase):
    """
    Test all views in lab
    """

    fixtures = ['core']

    def setUp(self):
        TestMeasurementsCreationForm().setUp()

        self.pt = Patient.objects.first()

        preclin_username = 'preclin-user'
        User = get_user_model()
        user = User.objects.create(username=preclin_username)
        user.set_password('password')
        user.save()
        self.user = get_object_or_404(User, username=preclin_username)

        g = Gender.objects.first()
        prov = Provider.objects.create(
        first_name="Jane", middle_name="M.", last_name="Doe",
        phone="111-222-3333", gender=g, associated_user=self.user)

        self.prov = prov

        coord_username = 'coordinator-user'
        user2 = User.objects.create(username=coord_username)
        change_perm = Permission.objects.get(codename='change_lab', content_type__app_label='labs')
        user2.user_permissions.add(change_perm)
        user2.set_password('password')
        user2.save()
        # Need to refetch user since permission change is cached
        self.user2 = get_object_or_404(User, username=coord_username)


    def test_default_permission(self):
        User = get_user_model()

        self.assertEqual(self.user.has_perm('labs.view_lab'), False)
        self.assertEqual(self.user.has_perm('labs.add_lab'), False)
        self.assertEqual(self.user.has_perm('labs.change_lab'), False)
        self.assertEqual(self.user.has_perm('labs.delete_lab'), False)

        # Add permission
        change_perm = Permission.objects.get(codename='change_lab', content_type__app_label='labs')
        self.user.user_permissions.add(change_perm)
        self.user.save()
        user = get_object_or_404(User, username=self.user.username)
        self.assertEqual(user.has_perm('labs.change_lab'), True)
        self.assertEqual(user.has_perm('change_lab'), False)

        # Remove permission
        user.user_permissions.remove(change_perm)
        user.save()
        user = get_object_or_404(User, username=self.user.username)
        self.assertEqual(user.has_perm('labs.change_lab'), False)
        user.save()
        self.user = get_object_or_404(User, username=self.user.username)


    def test_lab_list_view(self):
        log_in_user(self.client, build_user())
        url = reverse('labs:all-labs', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_lab_table_view(self):
        log_in_user(self.client, build_user())
        url = reverse('labs:all-labs-table', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_lab_detail_view(self):
        log_in_user(self.client, build_user())

        lt1 = LabType.objects.get(name='testlabtype')
        form_data = TestMeasurementsCreationForm().build_form(
            lab_type=lt1,
            lab_time=now(),
            pt = self.pt
            )
        form = forms.MeasurementsCreationForm(new_lab_type=lt1,
            pt=self.pt, data=form_data)
        if form.is_valid():
            form.save()

        new_lab = Lab.objects.filter(lab_type=lt1).first()
        url = reverse('labs:lab-detail', kwargs={'pk':new_lab.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        fake_pk = 0
        self.assertFalse(Lab.objects.filter(pk=fake_pk).exists())
        url = reverse('labs:lab-detail', kwargs={'pk':fake_pk})
        response = self.client.get(url)
        print(response)
        self.assertEqual(response.status_code, 404)


    def switch_user(self, current_provider, new_user):
        current_provider.associated_user = new_user
        updated_provider = log_in_user(self.client, current_provider)
        return updated_provider


    def test_lab_add_view_no_perm(self):
        User = get_user_model()

        provider = log_in_user(self.client, build_user())
        user = provider.associated_user

        # User can't view add lab page when having no permission
        self.assertFalse(user.has_perm('labs.add_lab'))
        url = reverse('labs:new-lab', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

        add_perm = Permission.objects.get(codename='add_lab', content_type__app_label='labs')
        user.user_permissions.add(add_perm)
        user.save()
        provider.associated_user = get_object_or_404(User, username=user.username)
        provider = log_in_user(self.client, provider)
        user = provider.associated_user

        self.assertTrue(user.has_perm('labs.add_lab'))
        url = reverse('labs:new-lab', kwargs={'pt_id':self.pt.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

