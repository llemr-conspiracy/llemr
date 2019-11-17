import datetime

from django.test import TestCase
from itertools import *

from django.core.urlresolvers import reverse
from django.utils.timezone import now

from followup.models import (
    ContactMethod, NoAptReason, NoShowReason, ContactResult)
from pttrack.models import (
    Gender, Patient, Provider, ProviderType, ReferralType, ReferralLocation
)

from . import forms
from . import models


class TestPatientContactForm(TestCase):
    """
    Tests the beahvior of the PatientContactForm which has a lot of
    complicated logic around valid form submission
    """

    fixtures = ['pttrack']

    def setUp(self):
        """ Provides the same context in all the tests """
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")
        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        reftype = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        refloc = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        refloc.care_availiable.add(reftype)

        self.referral = models.Referral.objects.create(
            comments="Needs his back checked",
            status=models.Referral.STATUS_PENDING,
            kind=reftype,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )
        self.referral.location.add(refloc)

        self.followup_request = models.FollowupRequest.objects.create(
            referral=self.referral,
            contact_instructions="Call him",
            due_date=datetime.date(2018, 9, 1),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )

        self.successful_res = ContactResult.objects.create(
            name="Got him", patient_reached=True)
        self.unsuccessful_res = ContactResult.objects.create(
            name="Disaster", patient_reached=False)
        # Need to update referral location
        self.referral_location = ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        self.noapt_reason = NoAptReason.objects.create(
            name="better things to do")
        self.noshow_reason = NoShowReason.objects.create(
            name="Hella busy.")

    def build_form(self, contact_successful, has_appointment, apt_location,
                   noapt_reason, pt_showed, noshow_reason):
        """Utility method used to construct a PatientContactForm to suit the
        needs of the testing subroutines based upon what is provided and not
        provided.
        """
        contact_resolution = (self.successful_res if contact_successful
                              else self.unsuccessful_res)

        form_data = {
            'contact_method': self.contact_method,
            'contact_status': contact_resolution
        }

        form_data['has_appointment'] = has_appointment
        form_data['pt_showed'] = pt_showed

        if apt_location:
            form_data['appointment_location'] = [ReferralLocation.objects.first().pk]

        if noapt_reason:
            form_data['no_apt_reason'] = self.noapt_reason

        if noshow_reason:
            form_data['no_show_reason'] = self.noshow_reason

        return forms.PatientContactForm(data=form_data)

    def test_has_appointment_and_pt_showed(self):
        """Verify that a provider is selected and no show and no appointment
        reasons are not selected. There are 8 cases tested here.
        """
        # correct: pt didn't show, noshow reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed=models.PatientContact.PTSHOW_YES)

        # No errors expected in this case
        self.assertEqual(len(form.errors), 0)

        # Create variable that holds those conditions that shouldn't lead to errors
        # apt_location = True
        # noapt_reason = False
        # noshow_reason = False
        proper_submission = (True, False, False)

        for form_field_provided in product([False, True], repeat=3):
            form = self.build_form(
                contact_successful=True,
                has_appointment=models.PatientContact.PTSHOW_YES,
                apt_location=form_field_provided[0],
                noapt_reason=form_field_provided[1],
                noshow_reason=form_field_provided[2],
                pt_showed=models.PatientContact.PTSHOW_YES)

            # Use an XOR to determine the number of differences between a
            # proper submission and the current combination of form fields
            expected_number_errors = sum(a ^ b for a, b in
                                         zip(form_field_provided,
                                             proper_submission))
            self.assertEqual(len(form.errors), expected_number_errors)

    def test_has_appointment_and_pt_no_show(self):
        """Verify that a provider is selected and a reason is provided for
        the no show. There are 8 cases tested here.
        """
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 0)

        # incorrect - no show reason is not supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 1)

        # incorrect - both apt location and no apt reason are supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=True,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 2)

        # incorrect - no appointment reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=True,
            noapt_reason=True,
            noshow_reason=True,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 1)

        # incorrect - appointment location is not selected
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=False,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 1)

        # incorrect - no show reason is not supplied, no apt location supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=False,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 2)

        # incorrect - no apt location and no apt reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=False,
            noapt_reason=True,
            noshow_reason=True,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 2)

        # incorrect - no show reason is not supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_YES,
            apt_location=False,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 3)

    def test_no_appointment(self):
        # first form contains a proper submission for the no appointment case
        form = self.build_form(
            contact_successful=True,
            has_appointment=models.PatientContact.PTSHOW_NO,
            apt_location=False,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed=models.PatientContact.PTSHOW_NO)

        self.assertEqual(len(form.errors), 0)

        # Create variable that holds those conditions that shouldn't lead to errors
        # apt_location = False
        # noapt_reason = True
        # noshow_reason = False
        proper_submission = (False, True, False)

        for form_field_provided in product([False, True], repeat=3):
            form = self.build_form(
                contact_successful=True,
                has_appointment=models.PatientContact.PTSHOW_NO,
                apt_location=form_field_provided[0],
                noapt_reason=form_field_provided[1],
                noshow_reason=form_field_provided[2],
                pt_showed=models.PatientContact.PTSHOW_NO)

            # Use an XOR to determine the number of differences between a
            # proper submission and the current combination of form fields
            expected_number_errors = sum(a ^ b for a, b in
                                         zip(form_field_provided,
                                             proper_submission))
            self.assertEqual(len(form.errors), expected_number_errors)

    def test_contact_unsuccessful(self):
        # Create a generic form
        contact_resolution = self.unsuccessful_res
        form_data = {
            'contact_method': self.contact_method,
            'contact_status': contact_resolution
        }

        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 0)

        # Progressively add errors to the form
        # If contact was unsuccessful, all these fields should be blank
        form_data['has_appointment'] = models.PatientContact.PTSHOW_YES
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 1)

        form_data['pt_showed'] = models.PatientContact.PTSHOW_YES
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 2)

        form_data['appointment_location'] = [ReferralLocation.objects.first().pk]
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 3)

        form_data['no_apt_reason'] = self.noapt_reason
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 4)

        form_data['no_show_reason'] = self.noshow_reason
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 5)

class TestSelectReferralType(TestCase):
    """Tests the select referral type page
    """

    fixtures = ['pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

    def test_select_referral_type_urls(self):
        """
        Verify that all the referral creation URLs are accessible.
        """
        # Create two different referral types
        reftype1 = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        reftype2 = ReferralType.objects.create(
            name="FQHC", is_fqhc=True)
        reftype3 = ReferralType.objects.create(
            name="Chiropractor", is_fqhc=False, is_active=False)

        # Check that select referral view
        url = reverse("select-referral-type",
                      args=(self.pt.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'href="%s"' % reverse("new-referral",
                            args=(self.pt.id, reftype1.slugify(),)))
        self.assertContains(response, 'href="%s"' % reverse("new-referral",
                            args=(self.pt.id, reftype2.slugify(),)))
        self.assertNotContains(response, 'href="%s"' % reverse("new-referral",
                               args=(self.pt.id, reftype3.slugify(),)))

        # Changing is_active to True should add reftype3 to list of choices
        reftype3.is_active = True
        reftype3.save()
        url = reverse("select-referral-type",
                      args=(self.pt.id,))
        response = self.client.get(url)
        self.assertContains(response, 'href="%s"' % reverse("new-referral",
                            args=(self.pt.id, reftype3.slugify(),)))


class TestCreateReferral(TestCase):
    """
    Tests the create referral page
    """
    fixtures = ['pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

    def test_location_list(self):
        """
        Verifies that the location list corresponding
        to a referral type are displayed
        """
        # Create two different referral types
        specialty = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        fqhc = ReferralType.objects.create(
            name="FQHC", is_fqhc=True)

        coh = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        podiatrist = ReferralLocation.objects.create(
            name='Podiatry', address='Euclid Ave.')
        fqhc1 = ReferralLocation.objects.create(
            name='FQHC1', address='Euclid Ave.')
        fqhc2 = ReferralLocation.objects.create(
            name='FQHC2', address='Euclid Ave.')

        coh.care_availiable.add(specialty)
        podiatrist.care_availiable.add(specialty)
        fqhc1.care_availiable.add(fqhc)
        fqhc2.care_availiable.add(fqhc)

        # Check if both FQHCs options are included if FQHC type is selected
        url = reverse('new-referral',
                      args=(self.pt.id, fqhc.slugify(),))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, fqhc1.name)
        self.assertContains(response, fqhc2.name)

        # Check if both Specialty referral options are on specialty referral page
        url = reverse('new-referral',
                      args=(self.pt.id, specialty.slugify(),))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, coh.name)
        self.assertContains(response, podiatrist.name)

    def test_referral_create_view(self):

        fqhc = ReferralType.objects.create(
            name="FQHC", is_fqhc=True)
        coh = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        coh.care_availiable.add(fqhc)
        coh.save()

        no_care_location = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')

        url = reverse('new-referral',
                      args=(self.pt.id, fqhc.slugify(),))
        response = self.client.post(
            url, {'location': coh.pk, 'comments': "asdf"},
            follow=True)

        self.assertTemplateUsed(response, 'referral/new-followup-request.html')
        self.assertEqual(models.Referral.objects.count(), 1)

        response = self.client.post(
            url, {'location': no_care_location.pk, 'comments': "asdf"},
            follow=True)
        self.assertTemplateUsed(response, 'referral/new-referral.html')
        self.assertEqual(models.Referral.objects.count(), 1)  # no change


class TestSelectReferral(TestCase):

    fixtures = ['pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        self.reftype = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        self.refloc = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        self.refloc.care_availiable.add(self.reftype)

    def test_referral_list(self):
        """
        Creates referrals and verifies that only appropriate ones are available
        in the select referral form
        """
        # Create pending referral with follow up request
        referral1 = models.Referral.objects.create(
            comments="Needs his back checked",
            status=models.Referral.STATUS_PENDING,
            kind=self.reftype,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )
        referral1.location.add(self.refloc)

        models.FollowupRequest.objects.create(
            referral=referral1,
            contact_instructions="Call him",
            due_date=datetime.date(2018, 11, 1),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )

        # Create pending referral without a follow up request
        reftype2 = ReferralType.objects.create(
            name="FQHC", is_fqhc=True)
        refloc2 = ReferralLocation.objects.create(
            name='Family Health Center', address='Euclid Ave.')
        refloc2.care_availiable.add(reftype2)
        referral2 = models.Referral.objects.create(
            comments="Needs his back checked",
            status=models.Referral.STATUS_PENDING,
            kind=reftype2,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )
        referral2.location.add(refloc2)

        # Create a referral for a different patient
        pt2 = Patient.objects.create(
            first_name="Arthur",
            last_name="Miller",
            middle_name="",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1994, 1, 22),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        reftype3 = ReferralType.objects.create(
            name="Dentist", is_fqhc=False)
        refloc3 = ReferralLocation.objects.create(
            name='Family Dental', address='Euclid Ave.')
        refloc3.care_availiable.add(reftype3)

        referral3 = models.Referral.objects.create(
            comments="Needs his back checked",
            status=models.Referral.STATUS_PENDING,
            kind=reftype3,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=pt2
        )
        referral3.location.add(refloc2)

        models.FollowupRequest.objects.create(
            referral=referral3,
            contact_instructions="Call him",
            due_date=datetime.date(2018, 11, 1),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=pt2
        )

        # Verify that there is only one referral available for the first patient
        url = reverse('select-referral',
                      args=(self.pt.id,))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, referral1)
        self.assertNotContains(response, referral2)
        self.assertNotContains(response, referral3)

        # Verify that the appropriate referral is available for the second patient
        url = reverse('select-referral',
                      args=(pt2.id,))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, referral1)
        self.assertNotContains(response, referral2)
        self.assertContains(response, referral3)

        # Change the first referral's status to successful
        # No referrals should be available for patient 1
        referral1.status = models.Referral.STATUS_SUCCESSFUL
        referral1.save()

        url = reverse('select-referral', args=(self.pt.id,))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, referral1)
        self.assertNotContains(response, referral2)
        self.assertNotContains(response, referral3)
        self.assertContains(
            response,
            '<a href="%s">create one?</a>' %
            reverse('select-referral-type', args=(self.pt.id,)))

        # submit the form and check that we redirect correctly if we
        # select a live referral
        response = self.client.post(
            reverse('select-referral', args=(pt2.id,)),
            {'referrals': referral3.pk},
            follow=True)

        self.assertTemplateUsed(response, 'referral/new-patient-contact.html')
        self.assertContains(response, pt2.first_name)

    def test_mark_done_link_on_patient_detail(self):
        """Check that FollowupRequests are on the patient-detail view.
        """

        ref = models.Referral.objects.create(
            patient=self.pt,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            comments="",
            status=models.Referral.STATUS_PENDING,
            kind=ReferralType.objects.first())
        ref.location.add(ReferralLocation.objects.first())
        ref.save()

        followup_request = models.FollowupRequest.objects.create(
            referral=ref,
            contact_instructions="Call him",
            due_date=(datetime.datetime.now().date() +
                      datetime.timedelta(days=2)),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )

        # request patient detail after creating a referral and followup
        # request, so that we should have the URL on patient-detail view.
        response = self.client.get(reverse('patient-detail',
                                           args=(ref.patient.pk,)))

        self.assertContains(response, followup_request.mark_done_url())


class TestPatientContactCreateView(TestCase):
    """Class for testing form_valid method in PatientContactCreate.
    """

    fixtures = ['pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.contact_result = ContactResult.objects.create(
            name="Reached on phone", patient_reached=True)

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        self.reftype = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        self.refloc = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        self.refloc.care_availiable.add(self.reftype)

        self.no_show_reason = NoShowReason.objects.create(name="Hella busy.")

    def test_valid_input(self):
        """ Validate that the form_valid method properly handles valid
        form input"""

        referral1 = models.Referral.objects.create(
            comments="Needs his back checked",
            status=models.Referral.STATUS_PENDING,
            kind=self.reftype,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )
        referral1.location.add(self.refloc)

        followup_request1 = models.FollowupRequest.objects.create(
            referral=referral1,
            contact_instructions="Call him",
            due_date=datetime.date(2018, 11, 1),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )

        buttons = [forms.PatientContactForm.SUCCESSFUL_REFERRAL,
                   forms.PatientContactForm.REQUEST_FOLLOWUP,
                   forms.PatientContactForm.UNSUCCESSFUL_REFERRAL]
        return_urls = [reverse('patient-detail', args=(self.pt.id,)),
                       reverse('new-followup-request', args=(self.pt.id,
                                                             referral1.id,)),
                       reverse('patient-detail', args=(self.pt.id,))]
        pt_showed = [models.PatientContact.PTSHOW_YES,
                     models.PatientContact.PTSHOW_NO,
                     models.PatientContact.PTSHOW_NO]

        for (button_clicked, correct_url, pt_show) in zip(buttons, return_urls,
                                                          pt_showed):
            form_data = {
                'contact_method': self.contact_method,
                'contact_status': self.contact_result,
                'has_appointment': models.PatientContact.PTSHOW_YES,
                'appointment_location': [self.refloc.pk],
                'pt_showed': pt_show,
                button_clicked: True
            }

            if pt_show == models.PatientContact.PTSHOW_NO:
                form_data['no_show_reason'] = self.no_show_reason

            n_patient_contact = models.PatientContact.objects.count()

            # Check that form is valid
            form = forms.PatientContactForm(data=form_data)
            self.assertEqual(form.is_valid(), True)

            # Verify that redirect goes to the right URL
            url = reverse('new-patient-contact', args=(self.pt.id,
                                                       referral1.id,
                                                       followup_request1.id))
            response = self.client.post(url, form_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, correct_url)
            self.assertEqual(models.PatientContact.objects.count(),
                             n_patient_contact + 1)

            # Check that the followup request has been marked as complete
            followup_request1 = models.FollowupRequest.objects.first()
            self.assertEqual(followup_request1.completion_date.date(),
                             now().date())

        url = reverse('select-referral', args=(referral1.patient.id,))
        response = self.client.get(url)
        self.assertContains(response, 'Oops!')
