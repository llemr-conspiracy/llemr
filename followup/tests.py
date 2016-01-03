'''Module for testing the followups Osler module.'''

import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

# For live tests.
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

from pttrack.models import Gender, Patient, Provider, ProviderType

from . import forms
from . import models
from . import urls

# pylint: disable=invalid-name


FU_TYPES = ["labs", "general", "vaccine"]


class FollowupLiveTesting(StaticLiveServerTestCase):
    fixtures = ['followup', 'pttrack']

    @classmethod
    def setUpClass(cls):
        super(FollowupLiveTesting, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(FollowupLiveTesting, cls).tearDownClass()

    def setUp(self):
        from pttrack.test_views import build_provider, live_submit_login

        build_provider(username='timmy', password='password',
                       roles=["Attending"])

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        live_submit_login(self.selenium, 'timmy', 'password')

    def verify_rendering(self, url, url_args=None, kwargs=None):
        if url_args is None and kwargs is None:
            self.selenium.get('%s%s' % (self.live_server_url,
                                        reverse(url)))
        elif url_args is None:
            self.selenium.get('%s%s' % (self.live_server_url,
                                        reverse(url, kwargs=kwargs)))
        else:
            self.selenium.get('%s%s' % (self.live_server_url,
                                        reverse(url, args=url_args)))

        jumbotron_elements = self.selenium.find_elements_by_xpath(
            '//div[@class="jumbotron"]')
        self.assertNotEqual(
            len(jumbotron_elements), 0,
            msg=" ".join(["Expected the URL ", url,
                          " to have a jumbotron element."]))

    def test_referral_followup_js_and_submission(self):
        '''
        Verify that the ReferralFollowup form is renderable, submittable, and
        that the javascript controlling the display of the various parameters
        is functioning. This includes 1) correct traversal of the decision
        tree and 2) correct clearing of parameters when we back up the tree.  
        '''
        from selenium.webdriver.support.ui import Select

        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('new-followup',
                                            args=(1, 'referral'))))

        

        elements = {}
        for element in ['contact_resolution', 'contact_method',
                        'referral_type', 'has_appointment', 'apt_location',
                        'pt_showed', 'noapt_reason', 'noshow_reason']:
            elements[element] = self.selenium.find_element_by_name(element)

        # Fill out the form, and test the js does what we want.
        Select(elements['contact_resolution']).select_by_value(
            str(models.ContactResult.objects.filter(attempt_again=False)[0]))
        Select(elements['contact_method']).select_by_index(1)
        Select(elements['referral_type']).select_by_index(1)

        COMMENT = "This is a comment."
        self.selenium.find_element_by_id("id_comments").send_keys(COMMENT)

        # 'has_appointment' starts off unchecked; verify initial state
        self.assertTrue(elements['noapt_reason'].is_displayed())
        self.assertTrue(not elements['pt_showed'].is_displayed())
        self.assertTrue(not elements['noshow_reason'].is_displayed())
        self.assertTrue(not elements['apt_location'].is_displayed())

        NOAPT_REASON = models.NoAptReason.objects.all()[0]
        Select(elements['noapt_reason']).select_by_visible_text(
            str(NOAPT_REASON))

        # double-tap on the 'has_appointment' should clear the state of 
        # 'noshow_reason' element
        elements['has_appointment'].click()
        elements['has_appointment'].click()

        self.assertNotEqual(
            str(NOAPT_REASON),
            Select(elements['noapt_reason']).first_selected_option.text)

        elements['has_appointment'].click()

        # with 'has_appointment' checked, we should now see pt_showed
        self.assertTrue(not elements['noapt_reason'].is_displayed())
        self.assertTrue(elements['pt_showed'].is_displayed())
        self.assertTrue(not elements['noshow_reason'].is_displayed())
        self.assertTrue(elements['apt_location'])

        APT_LOCATION = models.ReferralLocation.objects.all()[0]
        Select(elements['apt_location']).select_by_visible_text(str(
            APT_LOCATION))
        Select(elements['pt_showed']).select_by_value("Yes")

        # if we uncheck 'has_appointment', we go back to the initial state,
        # and lose the data we entered
        elements['has_appointment'].click()

        self.assertTrue(elements['noapt_reason'].is_displayed())
        self.assertTrue(not elements['pt_showed'].is_displayed())
        self.assertTrue(not elements['noshow_reason'].is_displayed())
        self.assertTrue(not elements['apt_location'].is_displayed())

        elements['has_appointment'].click()

        # we should lose the state of the apt_location SELECT.
        self.assertNotEqual(
            Select(elements['apt_location']).first_selected_option.text,
            str(APT_LOCATION))
        self.assertNotEqual(
            Select(elements['apt_location']).first_selected_option.text, "Yes")

        # re-set the state of the options
        Select(elements['apt_location']).select_by_visible_text(str(
            APT_LOCATION))
        Select(elements['pt_showed']).select_by_value("Yes")

        # if pt showed, no further data is required, visibility is as above.
        self.assertTrue(not elements['noapt_reason'].is_displayed())
        self.assertTrue(elements['pt_showed'].is_displayed())
        self.assertTrue(not elements['noshow_reason'].is_displayed())
        self.assertTrue(elements['apt_location'])

        Select(elements['pt_showed']).select_by_value("No")

        # if pt didn't show, noshow_reason appears.
        self.assertTrue(not elements['noapt_reason'].is_displayed())
        self.assertTrue(elements['pt_showed'].is_displayed())
        self.assertTrue(elements['noshow_reason'].is_displayed())
        self.assertTrue(elements['apt_location'])

        Select(elements['noshow_reason']).select_by_index(1)

        # attempt submission
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()

        # we should redirect
        self.assertEquals(
            ''.join([self.live_server_url,
                     reverse('patient-detail', args=(1,))]),
            self.selenium.current_url)

        # and the submission with this comment should be in the db
        self.assertGreater(
            models.ReferralFollowup.objects.\
                filter(comments=COMMENT).count(), 
            0)

    def test_followup_view_rendering(self):
        from django.core.urlresolvers import NoReverseMatch

        for url in urls.urlpatterns:
            if url.name in ['new-followup', 'followup']:
                continue

            # all the URLs have either one parameter or none. Try one
            # parameter first; if that fails, try with none.
            try:
                self.verify_rendering(url.name, (1,))
            except NoReverseMatch:
                self.verify_rendering(url.name)

        for fu_type in FU_TYPES:
            self.verify_rendering('new-followup', (1, fu_type))

        # TODO: build in checks for 'followup' once the objects exist.
        # for model in ['General', 'Lab']:
        #     self.verify_rendering('followup',
        #                           kwargs={"pk": 1, "model": model})


class TestReferralFollowupForms(TestCase):
    '''
    Test the validation and behavior of the forms used to do followups.
    '''
    
    def setUp(self):
        self.contact_method = models.ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.create(long_name="Male",
                                         short_name="M"),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        self.successful_res = models.ContactResult.objects.create(
            name="Got him", patient_reached=True)
        self.unsuccessful_res = models.ContactResult.objects.create(
            name="Disaster", patient_reached=False)
        self.reftype = models.ReferralType.objects.create(name="Chiropracter")
        self.referral_location = models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        self.noapt_reason = models.NoAptReason.objects.create(
            name="better things to do")
        self.noshow_reason = models.NoShowReason.objects.create(
            name="Hella busy.")


    def build_form(self, contact_successful, has_appointment, apt_location, noapt_reason, noshow_reason, pt_showed=None):
        '''
        Construct a ReferralFollowup form to suit the needs of the testing
        subroutines based upon what is provided and not provided.
        '''

        contact_resolution = self.successful_res if contact_successful else self.unsuccessful_res

        form_data = {
            'contact_method': self.contact_method,
            'contact_resolution': contact_resolution,
            'patient': self.pt,
            'referral_type': self.reftype,
            }

        # Has appointment could (at least in principle) be True, False, or
        # unspecified.
        if has_appointment:
            form_data['has_appointment'] = True
        elif has_appointment is None:
            pass
        else:
            form_data['has_appointment'] = False

        if apt_location:
            form_data['apt_location'] = self.referral_location.id

        if noapt_reason:
            form_data['noapt_reason'] = self.noapt_reason

        if pt_showed is None:
            pass
        elif pt_showed:
            form_data['pt_showed'] = 'Yes'
        else:
            form_data['pt_showed'] = 'No'

        if noshow_reason:
            form_data['noshow_reason'] = self.noshow_reason


        return forms.ReferralFollowup(data=form_data)

    def test_hasapt_pt_noshow(self):
        '''
        Test correct submission variations for a ReferralFollowup that has an
        appointment.
        '''

        # correct: pt didn't show, noshow reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=True,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed=False)

        self.assertEqual(len(form.errors), 0)

        # incorrect: pt didn't show and noshow reason is missing
        form = self.build_form(
            contact_successful=True,
            has_appointment=True,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed=False)

        self.assertGreater(len(form['noshow_reason'].errors), 0)

        # incorrect: pt showed and noshow reason is present
        form = self.build_form(
            contact_successful=True,
            has_appointment=True,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed=True)

        self.assertGreater(len(form['noshow_reason'].errors), 0)


    def test_correct_successful_noapt(self):
        '''
        Test a correct submission of ReferralFollowup when
        ContactResult.patient_reached is True but has_appointment is false.
        That is, apt_location and noapt_reason are provided.
        '''

        form = self.build_form(
            contact_successful=True,
            has_appointment=False,
            apt_location=True,
            noapt_reason=True,
            noshow_reason=False)

        self.assertEqual(len(form.errors), 0)

    def test_incorrect_successful_noapt(self):
        '''
        Test that a successful contact with no appointment that lacks a
        noapt_reason is considered incorrect.
        '''

        form = self.build_form(
            contact_successful=True,
            has_appointment=False,
            noapt_reason=False,
            apt_location=False,
            noshow_reason=False)

        self.assertGreater(len(form['noapt_reason'].errors), 0)

    def test_correct_unsuccssful_noapt(self):
        '''
        Test that an unsuccessful contact requires only has_appointment and
        referral_type. apt_location and noapt_reason are not required.
        '''

        form = self.build_form(
            contact_successful=False,
            has_appointment=None,
            apt_location=False,
            noapt_reason=False,
            noshow_reason=False)

        self.assertEqual(len(form.errors), 0)

    def test_incorrect_unsuccessful_noapt(self):
        '''
        Test that an unsuccessful contact with noapt and nowshow reasons will
        fail.
        '''

        form = self.build_form(
            contact_successful=False,
            has_appointment=None,
            apt_location=False,
            noapt_reason=True,
            noshow_reason=False)

        self.assertGreater(len(form['noapt_reason'].errors), 0)

        form = self.build_form(
            contact_successful=False,
            has_appointment=None,
            apt_location=False,
            noapt_reason=False,
            noshow_reason=True)

        self.assertGreater(len(form['noshow_reason'].errors), 0)


class FollowupTest(TestCase):
    fixtures = ['followup', 'pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

    def test_followup_view_urls(self):

        pt = Patient.objects.all()[0]

        method = models.ContactMethod.objects.create(name="Carrier Pidgeon")
        res = models.ContactResult(name="Fisticuffs")
        reftype = models.ReferralType.objects.create(name="Chiropracter")
        aptloc = models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        reason = models.NoAptReason.objects.create(
            name="better things to do")

        for i in range(101):
            # General Followup
            gf = models.GeneralFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=Provider.objects.all()[0],
                author_type=ProviderType.objects.all()[0],
                patient=pt)

            url = reverse('followup', kwargs={"pk": gf.id, "model": 'General'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Lab Followup
            lf = models.LabFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=Provider.objects.all()[0],
                author_type=ProviderType.objects.all()[0],
                patient=pt,
                communication_success=True)

            url = reverse('followup', kwargs={"pk": lf.id, "model": 'Lab'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Vaccine Followup
            vf = models.VaccineFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=Provider.objects.all()[0],
                author_type=ProviderType.objects.all()[0],
                patient=pt,
                subsq_dose=False)

            url = reverse('followup', kwargs={"pk": vf.id, "model": 'Vaccine'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Referral Followup
            rf = models.ReferralFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=Provider.objects.all()[0],
                author_type=ProviderType.objects.all()[0],
                patient=pt,
                referral_type=reftype,
                has_appointment=False,
                apt_location=aptloc,
                noapt_reason=reason)

            url = reverse('followup',
                          kwargs={"pk": rf.id, "model": 'Referral'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_followup_create_urls(self):
        '''
        Verify that all the followup creation URLs are accessible.
        '''
        pt = Patient.objects.all()[0]

        for fu_type in FU_TYPES:
            url = reverse("new-followup",
                          kwargs={"pt_id": pt.id, 'ftype': fu_type.lower()})

            response = self.client.get(url)
            self.assertEquals(response.status_code, 200)

        response = self.client.get(reverse("new-referral-followup",
                                           args=(pt.id,)))
        self.assertEquals(response.status_code, 200)

        url = reverse("followup", kwargs={"pk": pt.id, "model": "Lab"})

    def test_create_followups(self):

        attempt_again_cr = models.ContactResult.objects.create(
            name="didn't reach the pt",
            attempt_again=True)
        no_attempt_again_cr = models.ContactResult.objects.create(
            name="totally reached the pt",
            attempt_again=False)

        # Try creating a followup that requires re-contacts and one that does
        # not. Verification for correctness of the redirect is in verify_fu
        for contact_result in [attempt_again_cr, no_attempt_again_cr]:
            submitted_gen_fu = {
                "contact_method":
                    models.ContactMethod.objects.all()[0].pk,
                "contact_resolution": contact_result,
                "comments": ""
                }

            self.verify_fu(models.GeneralFollowup, 'general',
                           submitted_gen_fu)

            submitted_vacc_fu = dict(submitted_gen_fu)
            submitted_vacc_fu['subsq_dose'] = True
            submitted_vacc_fu['dose_date'] = str(datetime.date.today())

            self.verify_fu(models.VaccineFollowup, 'vaccine',
                           submitted_vacc_fu)

            submitted_lab_fu = dict(submitted_gen_fu)
            submitted_lab_fu["communication_success"] = True

            self.verify_fu(models.LabFollowup, 'labs',
                           submitted_lab_fu)

            submitted_ref_fu = dict(submitted_gen_fu)
            submitted_ref_fu.update(
                {"referral_type" : models.ReferralType.objects.all()[0].pk,
                 "has_appointment": True,
                 'apt_location': models.ReferralLocation.objects.all()[0].pk,
                 'pt_showed': "Yes",
                 'noapt_reason': "",
                 'noshow_reason': "",
                })

            self.verify_fu(models.ReferralFollowup, 'referral',
                           submitted_ref_fu)

    def verify_fu(self, fu_type, ftype, submitted_fu):

        pt = Patient.objects.all()[0]

        n_followup = len(fu_type.objects.all())

        url = reverse('new-followup', kwargs={"pt_id": pt.id,
                                              "ftype": ftype})
        response = self.client.post(url, submitted_fu)

        self.assertEqual(response.status_code, 302)

        if submitted_fu["contact_resolution"].attempt_again:
            self.assertRedirects(response,
                                 reverse("new-action-item", args=(pt.id,)))
        else:
            self.assertRedirects(response,
                                 reverse('patient-detail', args=(pt.id,)))

        self.assertEquals(len(fu_type.objects.all()), n_followup + 1)

        # this should get the most recently created followup, which should be
        # the one we just posted to create
        new_fu = sorted(fu_type.objects.all(), key=lambda(fu): fu.written_datetime)[-1]

        # make sure that all of the parameters in the submitted fu make it
        # into the object.
        for param in submitted_fu:
            if submitted_fu[param]:
                try:
                    self.assertEquals(str(submitted_fu[param]),
                                      str(getattr(new_fu, param)))
                except AssertionError:
                    self.assertEquals(submitted_fu[param],
                                      getattr(new_fu, param).pk)

