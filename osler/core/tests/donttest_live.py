import datetime

from django.urls import reverse
from django.utils.timezone import now

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from osler.pttack import models
from osler.core.tests.test_views import build_provider
from osler.core.tests.test import SeleniumLiveTestCase

from osler.workup import models as workup_models


BASIC_FIXTURE = 'core.json'


class LiveTesting(SeleniumLiveTestCase):
    fixtures = [BASIC_FIXTURE]

    def test_login(self):
        '''
        Test the login sequence for one clinical role and mulitiple clinical
        roles.
        '''

        build_provider(username='jrporter', password='password')

        # any valid URL should redirect to login at this point.
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login('jrporter', 'password')

        # now we should have to choose a clinical role
        self.assertEqual(self.selenium.current_url,
                          '%s%s%s' % (self.live_server_url,
                                      reverse('core:choose-clintype'),
                                      '?next=' +
                                      reverse('dashboard-dispatch')))

        self.selenium.find_element_by_xpath(
            '//input[@value="Coordinator"]').click()
        self.selenium.find_element_by_xpath(
            '//button[@type="submit"]').click()

        # import time
        # time.sleep(10)
        # self.selenium.get_screenshot_as_file('screencap.png')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "id_pt_1_activept")))

        self.assertEqual(self.selenium.current_url,
                          '%s%s' % (self.live_server_url, reverse('home')))

        self.selenium.get('%s%s' % (self.live_server_url, reverse('logout')))

        # make a provider with only one role.
        build_provider(username='timmy', password='password',
                       roles=["Attending"])

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login('timmy', 'password')

        # now we should be redirected directly to home.
        self.assertEqual(self.selenium.current_url,
                          '%s%s' % (self.live_server_url,
                                    reverse('dashboard-attending')))

    def test_core_patient_detail_collapseable(self):
        """Ensure that collapsable AI lists open and close with AIs inside
        """

        build_provider(username='timmy', password='password',
                       roles=["Attending"])
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login('timmy', 'password')

        ai_prototype = {
            'instruction': models.ActionInstruction.objects.first(),
            'comments': "",
            'author_type': models.ProviderType.objects.first(),
            'patient': models.Patient.objects.first()
        }

        models.ActionItem.objects.create(
            due_date=now().today(),
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        yesterday = now().date() - datetime.timedelta(days=1)
        models.ActionItem.objects.create(
            due_date=yesterday,
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('core:patient-detail', args=(1,))))

        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located(
                (By.ID, 'toggle-collapse5')))

        self.assertFalse(self.selenium.find_element_by_id('collapse5')
                                      .find_element_by_xpath('./ul/li')
                                      .is_displayed())

        self.assertEqual(
            len(self.selenium.find_element_by_id('collapse5')
                             .find_elements_by_xpath('./ul/li')),
            2)

        self.selenium.find_element_by_id('toggle-collapse5').click()

        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="panel-collapse collapse in"]')))

        self.assertEqual(
            len(self.selenium.find_element_by_id('collapse5')
                             .find_elements_by_xpath('./ul/li')),
            2)

        self.assertTrue(self.selenium.find_element_by_id('collapse5')
                                     .find_element_by_xpath('./ul/li')
                                     .is_displayed())

    def test_core_view_rendering(self):
        '''
        Test that core urls render correctly, as determined by the
        existance of a jumbotron at the top.
        '''
        from . import urls
        from django.urls import NoReverseMatch

        # build a provider and log in.
        build_provider(username='timmy', password='password',
                       roles=["Attending"])
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login('timmy', 'password')

        for url in urls.urlpatterns:
            # except 'choose-clintype' and action item modifiers from test
            # since they're redirects.
            if url.name in ['choose-clintype', 'done-action-item',
                            'reset-action-item', 'document-detail',
                            'document-update', 'update-action-item']:
                # TODO: add test data for documents so document-detail and
                # document-update can be tested as well.
                continue

            # all the URLs have either one parameter or none. Try one
            # parameter first; if that fails, try with none.
            try:
                self.selenium.get('%s%s' % (self.live_server_url,
                                            reverse(url.name, args=(1,))))
            except NoReverseMatch:
                self.selenium.get('%s%s' % (self.live_server_url,
                                            reverse(url.name)))

            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="jumbotron"]')))

            jumbotron_elements = self.selenium.find_elements_by_xpath(
                '//div[@class="jumbotron"]')
            self.assertNotEqual(
                len(jumbotron_elements), 0,
                msg=" ".join(["Expected the URL ", url.name,
                              " to have a jumbotron element."]))


class LiveTestPatientLists(SeleniumLiveTestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        # build a provider and log in
        self.provider_password = 'password'
        attending = build_provider(
            username='timmy_attend',
            password=self.provider_password,
            roles=["Attending"])
        coordinator = build_provider(
            username='timmy_coord',
            password=self.provider_password,
            roles=["Coordinator"])
        clinical = build_provider(
            username='timmy_clinical',
            password=self.provider_password,
            roles=["Clinical"])
        preclinical = build_provider(
            username='timmy_preclin',
            password=self.provider_password,
            roles=["Preclinical"])
        self.providers = {
            'attending': attending,
            'coordinator': coordinator,
            'clinical': clinical,
            'preclinical': preclinical
        }

        workup_models.ClinicType.objects.create(name="Basic Care Clinic")

        # various time references used in object creation
        tomorrow = now().date() + datetime.timedelta(days=1)
        yesterday = now().date() - datetime.timedelta(days=1)
        earlier_this_week = now().date() - datetime.timedelta(days=5)
        last_week = now().date() - datetime.timedelta(days=15)

        tomorrow_clindate = workup_models.ClinicDate.objects.create(
            clinic_type=workup_models.ClinicType.objects.first(),
            clinic_date=tomorrow)
        yesterday_clindate = workup_models.ClinicDate.objects.create(
            clinic_type=workup_models.ClinicType.objects.first(),
            clinic_date=yesterday)
        last_week_clindate = workup_models.ClinicDate.objects.create(
            clinic_type=workup_models.ClinicType.objects.first(),
            clinic_date=earlier_this_week)
        # log_in_provider(self.client, build_provider(["Attending"]))

        pt1 = models.Patient.objects.get(pk=1)
        pt1.toggle_active_status()
        pt1.save()
        self.pt1 = pt1

        pt_prototype = {
            'phone': '+49 178 236 5288',
            'gender': models.Gender.objects.all()[1],
            'address': 'Schulstrasse 9',
            'city': 'Munich',
            'state': 'BA',
            'zip_code': '63108',
            'pcp_preferred_zip': '63018',
            'date_of_birth': datetime.date(1990, 1, 1),
            'patient_comfortable_with_english': False,
            'preferred_contact_method': models.ContactMethod.objects.first(),
        }

        self.pt2 = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            **pt_prototype
        )

        self.pt3 = models.Patient.objects.create(
            first_name="Asdf",
            last_name="Lkjh",
            middle_name="Bayer",
            **pt_prototype
        )

        self.pt4 = models.Patient.objects.create(
            first_name="No",
            last_name="Action",
            middle_name="Item",
            **pt_prototype
        )

        self.pt5 = models.Patient.objects.create(
            first_name="No",
            last_name="Workup",
            middle_name="Patient",
            **pt_prototype
        )
        self.pt5.case_managers.add(coordinator)

        wu_prototype = {
            'chief_complaint': "SOB", 'diagnosis': "MI",
            'HPI': "", 'PMH_PSH': "", 'meds': "", 'allergies': "",
            'fam_hx': "", 'soc_hx': "",
            'ros': "", 'pe': "", 'A_and_P': "",
            'author': self.providers['coordinator'],
            'author_type': self.providers['coordinator'].clinical_roles.first(),
        }

        # Give self.pt2 a workup one day later.
        workup_models.Workup.objects.create(
            clinic_day=tomorrow_clindate,
            patient=self.pt2,
            **wu_prototype)

        # Give pt3 a workup one day ago.
        workup_models.Workup.objects.create(
            clinic_day=yesterday_clindate,
            patient=self.pt3,
            **wu_prototype)

        # Give pt1 a signed workup five days ago.
        workup_models.Workup.objects.create(
            clinic_day=last_week_clindate,
            patient=pt1,
            signer=self.providers['attending'],
            **wu_prototype)

        ai_prototype = {
            'author': self.providers['coordinator'],
            'author_type': self.providers['coordinator'].clinical_roles.first(),
            'instruction': models.ActionInstruction.objects.first(),
            'comments': ""
        }

        # make pt1 have and AI due tomorrow
        models.ActionItem.objects.create(
            due_date=tomorrow,
            patient=pt1,
            **ai_prototype)

        # make self.pt2 have an AI due yesterday
        models.ActionItem.objects.create(
            due_date=yesterday,
            patient=self.pt2,
            **ai_prototype)

        # make pt3 have an AI that during the test will be marked done
        models.ActionItem.objects.create(
            due_date=last_week,
            patient=self.pt3,
            **ai_prototype)

    def test_attestation_column(self):

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login(self.providers['coordinator'].username,
                          self.provider_password)

        self.selenium.get(
            '%s%s' % (self.live_server_url, reverse("core:all-patients")))

        pt_tbody = self.selenium.find_element_by_xpath(
            "//div[@class='container']/table/tbody")
        pt1_attest_status = pt_tbody.find_element_by_xpath("//tr[5]/td[6]")
        # attested note is marked as having been attested by the attending
        self.assertEqual(pt1_attest_status.text,
                          str(self.providers['attending']))

        # now a patient with no workup should have 'no note'
        pt4_attest_status = pt_tbody.find_element_by_xpath("//tr[2]/td[6]")
        self.assertEqual(pt4_attest_status.text, 'No Note')

        # now a patient with unattested workup should have 'unattested'
        pt2_attest_status = pt_tbody.find_element_by_xpath("//tr[3]/td[6]")
        self.assertEqual(pt2_attest_status.text, 'Unattested')

    def test_all_patients_correct_order(self):

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login(self.providers['coordinator'].username,
                          self.provider_password)

        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("core:all-patients")))

        # causes a broken pipe error
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("core:all-patients")))

        self.assertEqual(self.selenium.current_url,
                          '%s%s' % (self.live_server_url,
                                    reverse('core:all-patients')))

        # unsure how to test for multiple elements/a certain number of elements
        # WebDriverWait(self.selenium, 60).until(
        #     EC.presence_of_element_located((By.ID, "ptlast")))
        # WebDriverWait(self.selenium, 60).until(
        #     EC.presence_of_element_located((By.ID, "ptlatest")))

        # test ordered by last name
        # this line does throw an error if the id-ed element does not exist
        pt_tbody = self.selenium.find_element_by_xpath(
            "//div[@class='container']/table/tbody")
        first_patient_name = pt_tbody.find_element_by_xpath(
            "//tr[2]/td[1]").text
        second_patient_name = pt_tbody.find_element_by_xpath(
            "//tr[3]/td[1]").text
        self.assertLessEqual(first_patient_name, second_patient_name)
        self.assertEqual(first_patient_name, "Action, No I.")

        # # test order by latest activity
        # # more difficult to test attributes, I'm just testing that the first
        # # name is correct
        # pt_last_tbody = self.selenium.find_element_by_xpath(
        #     "//div[@id='ptlatest']/table/tbody")
        # first_patient_name = pt_last_tbody.find_element_by_xpath(
        #     ".//tr[2]/td[1]/a").get_attribute("text")
        # self.assertEqual(first_patient_name, "Brodeltein, Juggie B.")

    def test_provider_types_correct_home_order(self):
        """Verify that for each provider type, on the home page the
        expected tabs appear and the expected patients for in each tab
        appear in the correct order.
        """
        provider_tabs = {
            'attending': ['unsignedwu', 'activept'],
            'coordinator': ['activept', 'activeai', 'pendingai', 'unsignedwu',
                            'usercases'],
            'clinical': ['activept'],
            'preclinical': ['activept']
        }

        tab_patients = {
            'activeai': [self.pt3, self.pt2],
            'pendingai': [self.pt1],
            'unsignedwu': [self.pt2, self.pt3],
            'activept': [self.pt4, self.pt2, self.pt3, self.pt5],
            'usercases': [self.pt5],
        }

        for provider_type in provider_tabs:
            self.selenium.get('%s%s' % (self.live_server_url, '/'))
            self.submit_login(self.providers[provider_type].username,
                              self.provider_password)
            self.selenium.get('%s%s' % (self.live_server_url, reverse("home")))

            for tab_name in provider_tabs[provider_type]:
                WebDriverWait(self.selenium, 30).until(
                    EC.presence_of_element_located((By.ID, tab_name)))

                # examine each tab and get pk of expected and present patients.
                tbody = self.selenium.find_element_by_xpath(
                    "//div[@id='%s']/table/tbody" % tab_name)

                present_pt_names = [
                    t.get_attribute('text') for t in
                    tbody.find_elements_by_xpath(".//tr[*]/td[1]/a")
                ]

                expected_pt_names = [p.name() for p in tab_patients[tab_name]]

                self.assertEqual(present_pt_names, expected_pt_names)

            self.selenium.get(
                '%s%s' % (self.live_server_url, reverse('logout')))

    def test_all_patients_filter(self):
        """Test the All Patients view's filter box.

        We test the following:
            - Searching for a a patient's entire name
            = Clearing the search box
            - Searching for an upper case fragment of a patient's name
            - Searching for a coordinator's name
        """

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login(self.providers['coordinator'].username,
                          self.provider_password)
        self.selenium.get(
            '%s%s' % (self.live_server_url, reverse("core:all-patients")))

        # filter on the first patient's entire name
        filter_box = self.selenium.find_element_by_id(
            'all-patients-filter-input')
        filter_box.send_keys(self.pt1.first_name)

        def get_present_pt_names():
            """Grab all the present & displayed names from the table
            """
            tbody = self.selenium.find_element_by_id('all-patients-table')
            return [
                t.get_attribute('text') for t in
                tbody.find_elements_by_xpath(".//tr[*]/td[1]/a")
                if t.is_displayed()
            ]

        # only patient 1 should be present
        present_pt_names = get_present_pt_names()
        self.assertIn(str(self.pt1), present_pt_names)
        self.assertNotIn(str(self.pt2), present_pt_names)
        self.assertNotIn(str(self.pt3), present_pt_names)

        def clear_and_check(input_element):
            # clear the box
            for i in range(100):
                input_element.send_keys(Keys.BACK_SPACE)
            # input_element.send_keys(Keys.DELETE)

            # import time
            # time.sleep(600)

            # now all patients should be present
            present_pt_names = get_present_pt_names()
            for pt in [self.pt1, self.pt2, self.pt3, self.pt4, self.pt5]:
                self.assertIn(str(pt), present_pt_names)

        clear_and_check(filter_box)

        # fill the box with an upper case fragment
        filter_box.send_keys(self.pt2.first_name.upper()[0:3])

        # only pt2 should be there now
        present_pt_names = get_present_pt_names()
        self.assertNotIn(str(self.pt1), present_pt_names)
        self.assertIn(str(self.pt2), present_pt_names)
        self.assertNotIn(str(self.pt3), present_pt_names)

        clear_and_check(filter_box)
        filter_box.send_keys(self.providers['coordinator'].first_name)

        # check for pt with coordinator
        present_pt_names = get_present_pt_names()
        self.assertNotIn(str(self.pt1), present_pt_names)
        self.assertNotIn(str(self.pt2), present_pt_names)
        self.assertNotIn(str(self.pt3), present_pt_names)
        self.assertIn(str(self.pt5), present_pt_names)
