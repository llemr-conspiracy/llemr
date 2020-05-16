from django.urls import reverse

from osler.core.test import SeleniumLiveTestCase
from osler.followup import urls, models
from osler.followup.tests import FU_TYPES


class FollowupLiveTesting(SeleniumLiveTestCase):
    fixtures = ['followup', 'core']

    def setUp(self):
        from osler.core.test_views import build_provider

        build_provider(username='timmy', password='password',
                       roles=["Attending"])

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login('timmy', 'password')

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
        self.assertEqual(
            ''.join([self.live_server_url,
                     reverse('core:patient-detail', args=(1,))]),
            self.selenium.current_url)

        # and the submission with this comment should be in the db
        self.assertGreater(
            models.ReferralFollowup.objects.filter(comments=COMMENT).count(),
            0)

    def test_followup_view_rendering(self):
        from django.urls import NoReverseMatch

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
