import datetime

from django.urls import reverse
from django.utils.timezone import now

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from osler.core import models, urls
from osler.core.tests.test_views import build_user
from osler.core.tests.test import SeleniumLiveTestCase

from osler.workup import models as workup_models
#from osler.workup.tests.tests import wu_dict

from django.forms.models import model_to_dict


import osler.workup.tests.factories as workup_factories

from osler.users.models import User
import osler.users.tests.factories as user_factories
import osler.core.tests.factories as core_factories

import factory

BASIC_FIXTURES = ['core', 'workup']


class LiveTesting(SeleniumLiveTestCase):
    fixtures = BASIC_FIXTURES

    def test_login(self):
        '''
        Test the login sequence for one clinical role and mulitiple clinical
        roles.
        '''

        build_user(username='jrporter', password='password',
            group_factories=[user_factories.CaseManagerGroupFactory,
            user_factories.VolunteerGroupFactory]
        )

        # any valid URL should redirect to login at this point.
        self.get_homepage()
        self.submit_login('jrporter', 'password')

        # now we should have to choose a clinical role
        assert self.selenium.current_url == '%s%s%s' % (self.live_server_url,
                                      reverse('core:choose-role'),
                                      '?next=%s' % reverse('dashboard-dispatch'))

        self.selenium.find_element_by_xpath(
            '//input[@name="radio-roles"]').click()
        self.selenium.find_element_by_xpath(
            '//button[@type="submit"]').click()

        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "all-patients-table")))

        assert self.selenium.current_url == '%s%s' % (self.live_server_url, reverse('dashboard-active'))


        self.logout()

        # make a provider with only one role.
        build_user(username='timmy', password='password',
                       group_factories=[user_factories.AttendingGroupFactory])

        self.get_homepage()
        self.submit_login('timmy', 'password')

        # now we should be redirected directly to home.
        assert self.selenium.current_url == '%s%s' % (self.live_server_url,
                                    reverse('dashboard-active'))

    def test_core_patient_detail_collapseable(self):
        """Ensure that collapsable AI lists open and close with AIs inside
        """

        user = build_user(password='password',
                       group_factories=[user_factories.AttendingGroupFactory])
        self.get_homepage()
        self.submit_login(user.username, 'password')

        ai_prototype = {
            'instruction': models.ActionInstruction.objects.first(),
            'comments': "",
            'author_type': user.groups.first(),
            'patient': models.Patient.objects.first(),
            'author': user
        }

        models.ActionItem.objects.create(
            due_date=now().today(),
            **ai_prototype
        )

        yesterday = now().date() - datetime.timedelta(days=1)
        models.ActionItem.objects.create(
            due_date=yesterday,
            **ai_prototype
        )

        self.selenium.get('%s%s' % (self.live_server_url,
            reverse('core:patient-detail', args=(1,))))

        active_action_item_id = 'collapse8'

        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located(
                (By.ID, 'toggle-' + active_action_item_id)))

        assert not (self.selenium.find_element_by_id(active_action_item_id)
            .find_element_by_xpath('./ul/li')
            .is_displayed())

        assert len(self.selenium.find_element_by_id(active_action_item_id)
            .find_elements_by_xpath('./ul/li')) == 2

        self.selenium.find_element_by_id('toggle-' + active_action_item_id).click()

        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="panel-collapse collapse in"]')))

        assert len(self.selenium.find_element_by_id(active_action_item_id)
            .find_elements_by_xpath('./ul/li')) == 2

        assert (self.selenium.find_element_by_id(active_action_item_id)
            .find_element_by_xpath('./ul/li')
            .is_displayed())

    def test_core_view_rendering(self):
        '''
        Test that core urls render correctly, as determined by the
        existence of a jumbotron at the top.
        '''
        from django.urls import NoReverseMatch

        # build a provider and log in.
        user = build_user(password='password',
            group_factories=[user_factories.CaseManagerGroupFactory])
        self.get_homepage()
        self.submit_login(user.username, 'password')

        for url in urls.urlpatterns:
            # except 'core:choose-role' and action item modifiers from test
            # since they're redirects.

            if url.name in ['choose-role', 'done-action-item',
                            'reset-action-item', 'document-detail',
                            'document-update', 'update-action-item']:
                # TODO: add test data for documents so document-detail and
                # document-update can be tested as well.
                continue

            # all the URLs have either one parameter or none. Try one
            # parameter first; if that fails, try with none.
            try:
                self.selenium.get('%s%s' % (self.live_server_url,
                                            reverse("%s%s" % ("core:", url.name), args=(1,))))
            except NoReverseMatch:
                self.selenium.get('%s%s' % (self.live_server_url,
                                            reverse("%s%s" % ("core:", url.name))))

            WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="jumbotron"]')))

            jumbotron_elements = self.selenium.find_elements_by_xpath(
                '//div[@class="jumbotron"]')
            self.assertNotEqual(
                len(jumbotron_elements), 0,
                msg=" ".join(["Expected the URL ", url.name,
                              " to have a jumbotron element."]))


class LiveTestAllPatients(SeleniumLiveTestCase):
    fixtures = BASIC_FIXTURES

    def setUp(self):
        # build a user and log in
        self.password = 'password'
        attending = build_user(
            password=self.password,
            group_factories=[user_factories.AttendingGroupFactory])
        coordinator = build_user(
            password=self.password,
            group_factories=[user_factories.CaseManagerGroupFactory])
        volunteer = build_user(
            password=self.password,
            group_factories=[user_factories.VolunteerGroupFactory])
        self.users = {
            'attending': attending,
            'coordinator': coordinator,
            'volunteer': volunteer,
        }

        # various time references used in object creation
        tomorrow = now().date() + datetime.timedelta(days=1)
        yesterday = now().date() - datetime.timedelta(days=1)
        earlier_this_week = now().date() - datetime.timedelta(days=5)
        last_week = now().date() - datetime.timedelta(days=15)

        # log_in_provider(self.client, build_user(["Attending"]))
        self.pt1 = models.Patient.objects.get(pk=1)

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
            first_name="Jigie",
            last_name="Brozeltein",
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

        # use default values
        #wu_prototype = wu_dict()

        
        wu_prototype2 = workup_factories.WorkupFactory()
        wu_prototype3 = workup_factories.WorkupFactory()
        wu_prototype1 = workup_factories.WorkupFactory()

        #import pdb
        #pdb.set_trace()

        #wu_prototype = model_to_dict(wu)

        #ORIGINAL
        models.EncounterStatus.objects.create(name="HERE", is_active=True)

        # Give self.pt2 a workup one day later.

        wu_prototype2.encounter = models.Encounter.objects.create(patient = self.pt2, clinic_day = tomorrow, 
            status = models.EncounterStatus.objects.first())

        wu_prototype2.patient = self.pt2


        #original:
        #wu_prototype['encounter'] = models.Encounter.objects.create(
            #patient=self.pt2,
            #clinic_day=tomorrow,
            #status=models.EncounterStatus.objects.first())
        #wu_prototype['patient'] = self.pt2
        #workup_models.Workup.objects.create(**wu_prototype)

        # Give pt3 a workup one day ago.
        wu_prototype3.encounter = models.Encounter.objects.create(patient = self.pt3, clinic_day = yesterday,
            status = models.EncounterStatus.objects.first())
        wu_prototype3.patient = self.pt3


        #original
        #wu_prototype['encounter'] = models.Encounter.objects.create(
           # patient=self.pt3,
            #clinic_day=yesterday,
           # status=models.EncounterStatus.objects.first())
       # wu_prototype['patient'] = self.pt3
        #workup_models.Workup.objects.create(**wu_prototype)

        # Give pt1 a signed workup five days ago.
        wu_prototype1.encounter = models.Encounter.objects.create(patient = self.pt1, clinic_day = earlier_this_week,
            status = models.EncounterStatus.objects.first())
        wu_prototype1.patient = self.pt1
        wu_prototype1.signer = self.users['attending']
        
        #original
       # wu_prototype['encounter'] = models.Encounter.objects.create(
            #patient=self.pt1,
            #clinic_day=earlier_this_week,
            #status=models.EncounterStatus.objects.first())
        #wu_prototype['patient'] = self.pt1
        #wu_prototype['signer'] = self.users['attending']
        #workup_models.Workup.objects.create(**wu_prototype)

        ai_prototype = {
            'author': self.users['coordinator'],
            'author_type': self.users['coordinator'].groups.first(),
            'instruction': models.ActionInstruction.objects.first(),
            'comments': ""
        }

        # make pt1 have and AI due tomorrow
        models.ActionItem.objects.create(
            due_date=tomorrow,
            patient=self.pt1,
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

        self.get_homepage()
        self.submit_login(self.users['coordinator'].username,
                          self.password)

        self.selenium.get(
            '%s%s' % (self.live_server_url, reverse("core:all-patients")))

        pt_tbody = self.selenium.find_element_by_xpath(
            "//div[@class='container']/table/tbody")
        #PatientFactory makes a patient too 
        pt1_attest_status = pt_tbody.find_element_by_xpath("//tr[6]/td[6]")
        # attested note is marked as having been attested by the attending
        # assert pt1_attest_status.text == str(self.users['attending'])

        # now a patient with no workup should have 'no note'
        pt4_attest_status = pt_tbody.find_element_by_xpath("//tr[2]/td[6]")
        assert pt4_attest_status.text == 'No Note'

        # now a patient with unattested workup should have 'unattested'
        pt2_attest_status = pt_tbody.find_element_by_xpath("//tr[4]/td[6]")
        assert pt2_attest_status.text == 'Unattested'

    def test_all_patients_correct_order(self):

        self.get_homepage()
        self.submit_login(self.users['coordinator'].username,
            self.password)

        self.selenium.get('%s%s' % (self.live_server_url,
            reverse("core:all-patients")))

        self.selenium.get('%s%s' % (self.live_server_url,
            reverse("core:all-patients")))

        assert self.selenium.current_url == '%s%s' % (self.live_server_url,
            reverse('core:all-patients'))

        # TODO add wait statement

        # test ordered by last name
        # this line does throw an error if the id-ed element does not exist
        pt_tbody = self.selenium.find_element_by_xpath(
            "//div[@class='container']/table/tbody")
        first_patient_name = pt_tbody.find_element_by_xpath(
            "//tr[2]/td[1]").text
        second_patient_name = pt_tbody.find_element_by_xpath(
            "//tr[3]/td[1]").text
        assert first_patient_name <= second_patient_name
        assert first_patient_name == "Action, No I."

        # TODO test order by latest activity


    # TODO modernize to account for new homepage routing, permissions
    def donttest_provider_types_correct_home_order(self):
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
            self.get_homepage()
            self.submit_login(self.users[provider_type].username,
                              self.password)
            self.selenium.get('%s%s' % (self.live_server_url, reverse("home")))

            for tab_name in provider_tabs[provider_type]:
                WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
                    EC.presence_of_element_located((By.ID, tab_name)))

                # examine each tab and get pk of expected and present patients.
                tbody = self.selenium.find_element_by_xpath(
                    "//div[@id='%s']/table/tbody" % tab_name)

                present_pt_names = [
                    t.get_attribute('text') for t in
                    tbody.find_elements_by_xpath(".//tr[*]/td[1]/a")
                ]

                expected_pt_names = [p.name() for p in tab_patients[tab_name]]

                assert present_pt_names == expected_pt_names


    def test_all_patients_filter(self):
        """Test the All Patients view's filter box.

        We test the following:
            - Searching for a a patient's entire name
            = Clearing the search box
            - Searching for an upper case fragment of a patient's name
            - Searching for a coordinator's name
        """

        self.get_homepage()
        self.submit_login(self.users['coordinator'].username,
                          self.password)
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

        assert str(self.pt1) in present_pt_names
        assert str(self.pt2) not in present_pt_names
        assert str(self.pt3) not in present_pt_names

        def clear_and_check(input_element):
            # clear the box
            for i in range(100):
                input_element.send_keys(Keys.BACK_SPACE)

            # now all patients should be present
            present_pt_names = get_present_pt_names()
            for pt in [self.pt1, self.pt2, self.pt3, self.pt4, self.pt5]:
                assert str(pt) in present_pt_names

        clear_and_check(filter_box)

        # fill the box with an upper case fragment
        filter_box.send_keys(self.pt2.first_name.upper()[0:3])

        # only pt2 should be there now
        present_pt_names = get_present_pt_names()

        assert str(self.pt1) not in present_pt_names
        assert str(self.pt2) in present_pt_names
        assert str(self.pt3) not in present_pt_names

        clear_and_check(filter_box)
        filter_box.send_keys(str(self.users['coordinator']))

        # check for pt with coordinator
        present_pt_names = get_present_pt_names()

        assert str(self.pt1) not in present_pt_names
        assert str(self.pt2) not in present_pt_names
        assert str(self.pt3) not in present_pt_names
        assert str(self.pt5) in present_pt_names

