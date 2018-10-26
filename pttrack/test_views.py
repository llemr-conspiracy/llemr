import datetime
import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files import File
from django.core import mail
from django.core.management import call_command

# For live tests.
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from . import models
from .test import SeleniumLiveTestCase
from workup import models as workupModels
from followup.models import ContactResult
from referral.models import Referral, FollowupRequest, PatientContact
from referral.forms import PatientContactForm

# pylint: disable=invalid-name
# Whatever, whatever. I name them what I want.

BASIC_FIXTURE = 'pttrack.json'


def note_check(test, note, client, pt_pk):
    '''
    Helper method that verifies that a note is correctly written to the
    database. This should probably be broken out into its own unit test that
    directly interfaces with the form object.
    '''
    test.assertEquals(note.author.pk,
                      int(client.session['_auth_user_id']))

    test.assertEquals(client.session['clintype_pk'],
                      note.author_type.pk)

    test.assertEquals(note.patient.pk, pt_pk)

    test.assertLessEqual((now() - note.written_datetime).total_seconds(),
                         10)
    test.assertLessEqual((now() - note.last_modified).total_seconds(), 10)


def build_provider(roles=None, username=None, password='password', email=None):

    # TODO this is not preferred. Should swap None for '__all__'
    # this will require hunting down all the places this is called, though.
    if roles is None:
        roles = ["Coordinator", "Attending", "Clinical", "Preclinical"]

    provtypes = [models.ProviderType.objects.get(short_name=role)
                 for role in roles]

    if username is None:
        username = 'user'+str(User.objects.all().count())

    if email is None:
        email = 'tommyljones@gmail.com'
    user = User.objects.create_user(
        username,
        email, password)
    user.save()

    g = models.Gender.objects.first()
    prov = models.Provider.objects.create(
        first_name="Tommy", middle_name="Lee", last_name="Jones",
        phone="425-243-9115", gender=g, associated_user=user)

    coordinator_provider = models.ProviderType.objects.all()[2]
    coordinator_provider.staff_view = True
    coordinator_provider.save()

    prov.clinical_roles.add(*provtypes)
    prov.save()
    user.save()

    assert len(roles) == prov.clinical_roles.count()
    assert user.provider is not None

    return user.provider


def log_in_provider(client, provider):
    ''' Creates a provider and logs them in. Role defines their provider_type,
    default is all '''

    user = provider.associated_user

    client.login(username=user.username, password='password')

    session = client.session
    session['clintype_pk'] = user.provider.clinical_roles.first().pk
    session.save()

    return user.provider


def get_url_pt_list_identifiers(self, url):
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

    list_identifiers = []
    pt_lists = json.loads(response.context['lists'])
    for pt_list in pt_lists:
        list_identifiers.append(pt_list['identifier'])
    return list_identifiers


class SendEmailTest(TestCase):
    fixtures = [BASIC_FIXTURE]
    '''
    Test custom django management command sendemail
    '''
    def setUp(self):
        #make 2 providers
        log_in_provider(self.client, build_provider(roles=["Coordinator"], email='user1@gmail.com'))
        log_in_provider(self.client, build_provider(roles=["Coordinator"], email='user2@gmail.com'))
        log_in_provider(self.client, build_provider(roles=["Coordinator"], email='user3@gmail.com'))

        pt = models.Patient.objects.first()
        pt.case_managers.add(models.Provider.objects.first())
        pt.case_managers.add(models.Provider.objects.all()[2])

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")

        tomorrow = now().date() + datetime.timedelta(days=1)
        yesterday = now().date() - datetime.timedelta(days=1)

        ai_prototype = {
        'instruction':ai_inst,
        'comments':"",
        'author_type':models.ProviderType.objects.first(),
        'patient':pt
        }

        #action item due today
        ai_today = models.ActionItem.objects.create(
            due_date=now().today(),
            author=models.Provider.objects.first(),
            **ai_prototype
            )

        #action item due yesterday
        ai_yesterday = models.ActionItem.objects.create(
            due_date=yesterday,
            author=models.Provider.objects.first(),
            **ai_prototype
            )

        #action item due tomorrow
        ai_tomorrow = models.ActionItem.objects.create(
            due_date=tomorrow,
            author=models.Provider.objects.all()[1],
            **ai_prototype
            )

        #complete action item from yesterday
        ai_complete = models.ActionItem.objects.create(
            due_date=yesterday,
            author=models.Provider.objects.all()[1],
            completion_date = now(),
            completion_author=models.Provider.objects.first(),
            **ai_prototype
            )

    def test_sendemail(self):
        '''
        Verifies that email is correctly being sent for incomplete,
        overdue action items
        '''
        call_command('action_item_spam')

        #test that 1 message has been sent for the AI due yesterday and today
        #but only 1 email bc same pt/case manager
        self.assertEqual(len(mail.outbox), 1)

        #verify that subject is correct
        self.assertEqual(mail.outbox[0].subject, 'SNHC: Action Item Due')

        #verify that the 1 message is to user1 and user3 (second case manager)
        self.assertEqual(mail.outbox[0].to, ['user1@gmail.com', 'user3@gmail.com'])


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
        self.assertEquals(self.selenium.current_url,
                          '%s%s%s' % (self.live_server_url,
                                      reverse('choose-clintype'),
                                      '?next='+reverse('home')))

        self.selenium.find_element_by_xpath(
            '//input[@value="Coordinator"]').click()
        self.selenium.find_element_by_xpath(
            '//button[@type="submit"]').click()

        # import time
        # time.sleep(10)
        # self.selenium.get_screenshot_as_file('screencap.png')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "id_pt_1_activept")))

        self.assertEquals(self.selenium.current_url,
                          '%s%s' % (self.live_server_url, reverse('home')))

        self.selenium.get('%s%s' % (self.live_server_url, reverse('logout')))

        # make a provider with only one role.
        build_provider(username='timmy', password='password',
                       roles=["Attending"])

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login('timmy', 'password')

        # now we should be redirected directly to home.
        self.assertEquals(self.selenium.current_url,
                          '%s%s' % (self.live_server_url,
                                    reverse('home')))

    def test_pttrack_view_rendering(self):
        '''
        Test that pttrack urls render correctly, as determined by the
        existance of a jumbotron at the top.
        '''
        from . import urls
        from django.core.urlresolvers import NoReverseMatch

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
            'attending' : attending,
            'coordinator' : coordinator,
            'clinical' : clinical,
            'preclinical' : preclinical
        }

        workupModels.ClinicType.objects.create(name="Basic Care Clinic")

        # various time references used in object creation
        tomorrow = now().date() + datetime.timedelta(days=1)
        yesterday = now().date() - datetime.timedelta(days=1)
        earlier_this_week = now().date() - datetime.timedelta(days=5)
        last_week = now().date() - datetime.timedelta(days=15)

        tomorrow_clindate = workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.first(),
            clinic_date=tomorrow,
            gcal_id="tmp")
        yesterday_clindate = workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.first(),
            clinic_date=yesterday,
            gcal_id="tmp")
        last_week_clindate = workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.first(),
            clinic_date=earlier_this_week,
            gcal_id="tmp")
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
            'date_of_birth': datetime.date(1990, 01, 01),
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
        workupModels.Workup.objects.create(
            clinic_day=tomorrow_clindate,
            patient=self.pt2,
            **wu_prototype)

        # Give pt3 a workup one day ago.
        workupModels.Workup.objects.create(
            clinic_day=yesterday_clindate,
            patient=self.pt3,
            **wu_prototype)

        # Give pt1 a signed workup five days ago.
        workupModels.Workup.objects.create(
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
            '%s%s' % (self.live_server_url, reverse("all-patients")))

        pt_tbody = self.selenium.find_element_by_xpath("//div[@class='container']/table/tbody")
        pt1_attest_status = pt_tbody.find_element_by_xpath("//tr[5]/td[6]")
            # attested note is marked as having been attested by the attending
        self.assertEquals(pt1_attest_status.text, str(self.providers['attending']))

            # now a patient with no workup should have 'no note'
        pt4_attest_status = pt_tbody.find_element_by_xpath("//tr[2]/td[6]")
        self.assertEquals(pt4_attest_status.text, 'No Note')

            # now a patient with unattested workup should have 'unattested'
        pt2_attest_status = pt_tbody.find_element_by_xpath("//tr[3]/td[6]")
        self.assertEquals(pt2_attest_status.text, 'Unattested')

    def test_all_patients_correct_order(self):

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.submit_login(self.providers['coordinator'].username,
                          self.provider_password)

        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("all-patients")))

        # causes a broken pipe error
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("all-patients")))

        self.assertEquals(self.selenium.current_url,
                          '%s%s' % (self.live_server_url,
                                    reverse('all-patients')))

        # unsure how to test for multiple elements/a certain number of elements
        # WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "ptlast")))
        # WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "ptlatest")))

        # test ordered by last name
        pt_tbody = self.selenium.find_element_by_xpath("//div[@class='container']/table/tbody") # this line does throw an error if the id-ed element does not exist
        first_patient_name = pt_tbody.find_element_by_xpath("//tr[2]/td[1]").text
        second_patient_name = pt_tbody.find_element_by_xpath("//tr[3]/td[1]").text
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
            'activeai': [self.pt2, self.pt3],
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
            '%s%s' % (self.live_server_url, reverse("all-patients")))

        # filter on the first patient's entire name
        filter_box = self.selenium.find_element_by_id('all-patients-filter-input')
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


class ViewsExistTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider())

    def test_basic_urls(self):
        basic_urls = ["home",
                      "all-patients",
                      "intake"]

        for basic_url in basic_urls:
            response = self.client.get(reverse(basic_url))
            self.assertEqual(response.status_code, 200)

    def test_initial_config(self):
        session = self.client.session
        del session['clintype_pk']
        session.save()

        # verify: no clinic date -> create clinic date
        response = self.client.get(reverse('all-patients'))
        self.assertRedirects(response,
                             reverse('choose-clintype')+"?next="+reverse('all-patients'))

        # verify: no provider -> provider creation
        # (now done in ProviderCreateTest)

        # verify: not logged in -> log in
        self.client.logout()
        response = self.client.get(reverse('all-patients'))
        self.assertRedirects(response, reverse('login')+'?next='+reverse('all-patients'))

    def test_pt_urls(self):
        pt_urls = ['patient-detail',
                   "new-clindate",
                   'new-action-item',
                   'followup-choice',
                   'patient-update']

        pt_urls_redirect = ['patient-activate-detail',
                            'patient-activate-home']

        pt = models.Patient.objects.first()

        for pt_url in pt_urls:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError as e:
                raise e

        for pt_url in pt_urls_redirect:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            try:
                self.assertEqual(response.status_code, 302)
            except AssertionError as e:
                raise e

    def test_provider_urls(self):
        response = self.client.get(reverse('new-provider'))
        self.assertEqual(response.status_code, 200)

    def test_document_urls(self):
        '''
        Test the views showing documents, as well as the integrity of path
        saving in document creation (probably superfluous).
        '''
        import os

        self.test_img = 'media/test.jpg'

        url = reverse('new-document', args=(1,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        dtype = models.DocumentType.objects.create(name="Silly Picture")

        doc = models.Document.objects.create(
            title="who done it?",
            comments="Pictured: silliness",
            document_type=dtype,
            image=File(open(self.test_img)),
            patient=models.Patient.objects.get(id=1),
            author=models.Provider.objects.get(id=1),
            author_type=models.ProviderType.objects.first())

        p = models.Document.objects.get(id=1).image.path
        random_name = p.split("/")[-1]
        random_name = random_name.split(".")[0]
        self.failUnless(open(p), 'file not found')
        self.assertEqual(doc.image.path, p)
        self.assertTrue(os.path.isfile(p))

        # Checking to make sure the path is 48 characters (the length of the random password

        self.assertEqual(len(random_name), 48)


        url = reverse('document-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # test the creation of many documents, just in case.
        for i in range(101):
            doc = models.Document.objects.create(
                title="who done it? "+str(i),
                comments="Pictured: silliness",
                document_type=dtype,
                image=File(open(self.test_img)),
                patient=models.Patient.objects.get(id=1),
                author=models.Provider.objects.get(id=1),
                author_type=models.ProviderType.objects.first())

            p = models.Document.objects.get(id=doc.pk).image.path
            random_name = p.split("/")[-1]
            random_name = random_name.split(".")[0]
            self.failUnless(open(p), 'file not found')
            self.assertEqual(doc.image.path, p)
            self.assertTrue(os.path.isfile(p))

            # Checking to make sure the path is 48 characters (the length of the random password

            self.assertEqual(len(random_name), 48)

            url = reverse('document-detail', args=(doc.pk,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            url = reverse('document-detail', args=(doc.pk,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            os.remove(p)
            self.assertFalse(os.path.isfile(p))


class ProviderCreateTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider())

    def test_provider_creation(self):
        """Verify that, in the absence of a provider, a provider is created,
        and that it is created correctly."""

        final_url = reverse('all-patients')

        # verify: no provider -> create provider
        models.Provider.objects.all().delete()
        response = self.client.get(final_url)
        final_response_url = response.url
        self.assertRedirects(response, reverse('new-provider')+'?next='+final_url)

        n_provider = len(models.Provider.objects.all())

        # The data submitted by a User when creating the Provider.
        form_data = {
            'first_name': "John",
            'last_name': "James",
            'phone': "8888888888",
            'languages': models.Language.objects.first().pk,
            'gender': models.Gender.objects.first().pk,
            'provider_email': "jj@wustl.edu",
            'clinical_roles': models.ProviderType.objects.first().pk,
        }
        response = self.client.post(response.url, form_data)
        # redirects anywhere; don't care where (would be the 'next' parameter)
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(models.Provider.objects.all()), n_provider + 1)

        new_provider = list(models.Provider.objects.all())[-1]

        # verify the writethrough
        for name in ['first_name', 'last_name']:
            self.assertEquals(getattr(new_provider, name),
                              getattr(new_provider.associated_user, name))
        self.assertEquals(form_data['provider_email'],
                          new_provider.associated_user.email)

        # now verify we're redirected
        response = self.client.get(final_url)
        self.assertEquals(response.status_code, 200)

        # Test for proper resubmission behavior.
        n_provider = len(models.Provider.objects.all())
        WebDriver().back()

        # POST a form with new names
        form_data['first_name'] = 'Janet'
        form_data['last_name'] = 'Jane'
        response = self.client.post(final_response_url, form_data)

        # Verify redirect anywhere; don't care where (would be the 'next' parameter)
        self.assertEqual(response.status_code, 302)

        # Verify that number of providers has not changed, and user's names is still the original new_provider's names
        self.assertEquals(len(models.Provider.objects.all()), n_provider)
        for name in ['first_name', 'last_name']:
            self.assertEquals(getattr(new_provider, name),
                              getattr(new_provider.associated_user, name))

        # now verify we're redirected
        response = self.client.get(final_url)
        self.assertEquals(response.status_code, 200)


class ProviderTypeTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def test_home_pt_list_types(self):
        url = reverse("home")

        log_in_provider(self.client, build_provider(["Coordinator"]))
        self.assertEqual(
            get_url_pt_list_identifiers(self, url),
            ['activept', 'priorityai', 'activeai', 'pendingai', 'unsignedwu', 'usercases'])

        log_in_provider(self.client, build_provider(["Attending"]))
        self.assertEqual(
            get_url_pt_list_identifiers(self, url),
            ['unsignedwu', 'activept'])

        log_in_provider(self.client, build_provider(["Clinical"]))
        self.assertEqual(get_url_pt_list_identifiers(self, url), ['activept'])

        log_in_provider(self.client, build_provider(["Preclinical"]))
        self.assertEqual(get_url_pt_list_identifiers(self, url), ['activept'])


class IntakeTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider())

        self.valid_pt_dict = {
            'first_name': "Juggie",
            'last_name': "Brodeltein",
            'middle_name': "Bayer",
            'phone': '+49 178 236 5288',
            'languages': [models.Language.objects.first()],
            'gender': models.Gender.objects.first().pk,
            'address': 'Schulstrasse 9',
            'city': 'Munich',
            'state': 'BA',
            'country': 'Germany',
            'zip_code': '63108',
            'pcp_preferred_zip': '63018',
            'date_of_birth': datetime.date(1990, 01, 01),
            'patient_comfortable_with_english': False,
            'ethnicities': [models.Ethnicity.objects.first()],
            'preferred_contact_method':
                models.ContactMethod.objects.first().pk
        }

    def preintake_patient_with_collision(self):

        self.valid_pt_dict['gender'] = models.Gender.objects.first()
        del self.valid_pt_dict['preferred_contact_method']
        del self.valid_pt_dict['languages']
        del self.valid_pt_dict['ethnicities']

        pt = models.Patient.objects.create(**self.valid_pt_dict)

        url = reverse('preintake')
        response = self.client.post(
            url,
            {k: self.valid_pt_dict[k] for k
             in ['first_name', 'last_name']},
            follow=True)

        self.assertTemplateUsed(response, 'pttrack/preintake-select.html')

        print(dir(response))
        print(response.context_data)

        self.assertIn(pt, response.context_data['object_list'])

    def preintake_patient_no_collision(self):

        url = reverse('preintake')
        response = self.client.post(
            url,
            {k: self.valid_pt_dict[k] for k
             in ['first_name', 'last_name']},
            follow=True)

        self.assertTemplateUsed(response, 'pttrack/intake.html')

        self.assertEquals(
            response.context_data['form']['first_name'].value(),
            self.valid_pt_dict['first_name'])

        self.assertEquals(
            response.context_data['form']['last_name'].value(),
            self.valid_pt_dict['last_name'])

    def test_can_intake_pt(self):

        n_pt = len(models.Patient.objects.all())

        submitted_pt = self.valid_pt_dict

        url = reverse('intake')

        response = self.client.post(url, submitted_pt)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.Patient.objects.count(), n_pt + 1)

        new_pt = models.Patient.objects.last()

        for param in submitted_pt:
            try:
                self.assertEquals(str(submitted_pt[param]),
                                  str(getattr(new_pt, param)))
            except AssertionError:
                self.assertEquals(str(submitted_pt[param]),
                                  str(getattr(new_pt, param).all()))

        # new patients should be marked as active by default
        self.assertTrue(new_pt.needs_workup)


class ActionItemTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider(["Coordinator"]))

    def test_action_item_urls(self):
        pt = models.Patient.objects.first()

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")
        ai = models.ActionItem.objects.create(
            instruction=ai_inst,
            due_date=now().today(),
            comments="",
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=pt)

        # new action items should not be done
        self.assertFalse(ai.done())

        # submit a request to mark the new ai as done. should redirect to
        # choose a followup type.
        ai_url = 'done-action-item'
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("followup-choice", args=(ai.patient.pk,)),
                      response.url)
        self.assertTrue(models.ActionItem.objects.first().done())
        self.assertEquals(models.ActionItem.objects.first().author.pk,
                          int(self.client.session['_auth_user_id']))
        self.assertNotEqual(
            models.ActionItem.objects.first().written_datetime,
            models.ActionItem.objects.first().last_modified)

        # submit a request to reset the ai. should redirect to pt
        ai_url = 'reset-action-item'
        prev_mod_datetime = models.ActionItem.objects.first().last_modified
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(pt.id,)),
                      response.url)
        self.assertFalse(models.ActionItem.objects.first().done())

        self.assertNotEqual(
            models.ActionItem.objects.first().written_datetime,
            models.ActionItem.objects.first().last_modified)
        self.assertNotEqual(prev_mod_datetime,
                            models.ActionItem.objects.first().last_modified)

        # make sure updating the action items url works
        ai_url = 'update-action-item'
        response = self.client.get(reverse(ai_url, args=(ai.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_create_action_item(self):

        self.assertEquals(len(models.ActionItem.objects.all()), 0)

        submitted_ai = {
            "instruction": models.ActionInstruction.objects.first().pk,
            "due_date": str(datetime.date.today() + datetime.timedelta(10)),
            "comments": "models.CharField(max_length=300)" # arbitrary string
            }

        url = reverse('new-action-item', kwargs={'pt_id': 1})
        response = self.client.post(url, submitted_ai)

        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(1,)), response.url)

        self.assertEquals(len(models.ActionItem.objects.all()), 1)
        new_ai = models.ActionItem.objects.first()

        submitted_ai['due_date'] = datetime.date(
            *([int(i) for i in submitted_ai['due_date'].split('-')]))

        for param in submitted_ai:
            self.assertEquals(str(submitted_ai[param]),
                              str(getattr(new_ai, param)))

        note_check(self, new_ai, self.client, 1)

class ProviderUpdateTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def test_require_providers_update(self):
        '''
        Test that the require_providers_update() method sets all needs_update to True
        '''
        provider = build_provider(username='jrporter', password='password', roles=['Preclinical']) # this line is repeated for every test instead of in a setUp def so that we can store the provider variable
        log_in_provider(self.client, provider)
        for provider in models.Provider.objects.all():
            self.assertEqual(provider.needs_updating, False)

        models.require_providers_update()

        for provider in models.Provider.objects.all():
            self.assertEqual(provider.needs_updating, True)

    def test_redirect_and_form_submit(self):
        '''
        Test correct redirect and form submit behavior
        '''
        final_url = reverse('home')

        provider = build_provider(username='jrporter', password='password', roles=['Preclinical'])
        log_in_provider(self.client, provider)
        initial_num_providers = models.Provider.objects.count()
        provider_pk = provider.pk

        # Verify needs_update -> will redirect
        models.require_providers_update()
        self.assertEqual(models.Provider.objects.get(pk=provider_pk).needs_updating, True)
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.context[0]['form'].initial['provider_email'], 'tommyljones@gmail.com')
        self.assertRedirects(response, reverse('provider-update')+"?next="+final_url)

        form_data = {
            'first_name': "John",
            'last_name': "James",
            'phone': "8888888888",
            'languages': models.Language.objects.first().pk,
            'gender': models.Gender.objects.first().pk,
            'provider_email': "jj@wustl.edu",
            'clinical_roles': ['Clinical'],
        }
        response = self.client.post(response.redirect_chain[0][0], form_data)

        # Redirects anywhere; don't care where (would be the 'next' parameter)
        self.assertEqual(response.status_code, 302)

        # Verify number of providers is still the same
        self.assertEqual(models.Provider.objects.count(), initial_num_providers)

        # Verify write-through and no longer needs update
        provider = models.Provider.objects.get(pk=provider_pk)
        roles = [role.short_name for role in getattr(provider,'clinical_roles').all()]
        self.assertEqual(roles, ['Clinical'])
        self.assertEqual(getattr(provider, 'phone'), '8888888888')
        self.assertEqual(getattr(provider, 'needs_updating'), False)

        # Verify that accessing final url no longer redirects
        response = self.client.get(final_url)
        self.assertEqual(response.status_code, 200)

class TestReferralPatientDetailIntegration(TestCase):
    """ Tests integration of Action Items and Referral Followups in patient-detail."""
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider())

        self.contact_method = models.ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        self.pt.case_managers.add(models.Provider.objects.first())

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")

        self.tomorrow = now().date() + datetime.timedelta(days=1)
        self.yesterday = now().date() - datetime.timedelta(days=1)

        ai_prototype = {
            'instruction': ai_inst,
            'comments': "",
            'author_type': models.ProviderType.objects.first(),
            'patient': self.pt
        }

        # Action item due today
        ai_today = models.ActionItem.objects.create(
            due_date=now().date(),
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        # Action item due yesterday
        ai_yesterday = models.ActionItem.objects.create(
            due_date=self.yesterday,
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        # Action item due tomorrow
        ai_tomorrow = models.ActionItem.objects.create(
            due_date=self.tomorrow,
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        # Complete action item from yesterday
        ai_complete = models.ActionItem.objects.create(
            due_date=self.yesterday,
            author=models.Provider.objects.first(),
            completion_date=now(),
            completion_author=models.Provider.objects.first(),
            **ai_prototype
        )

        self.reftype = models.ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        self.refloc = models.ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        self.refloc.care_availiable.add(self.reftype)

    def test_patient_detail(self):
        """ Creates several action items and referral followups to check if view
            is properly supplying Status, FQHC Referral Status, Referrals,
            Action Item totals, and Followup totals."""

        # Create follow up request due yesterday
        referral1 = Referral.objects.create(
            comments="Needs his back checked",
            status=Referral.STATUS_PENDING,
            kind=self.reftype,
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )
        referral1.location.add(self.refloc)

        followup_request1 = FollowupRequest.objects.create(
            referral=referral1,
            contact_instructions="Call him",
            due_date=self.yesterday,
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )

        # Create a second referral followup request due today
        fqhc_reftype = models.ReferralType.objects.create(
            name="FQHC", is_fqhc=True)
        fhc = models.ReferralLocation.objects.create(
            name="Family Health Center", address="Manchester Ave.")
        fhc.care_availiable.add(fqhc_reftype)

        referral2 = Referral.objects.create(
            comments="Connecting patient to FQHC",
            status=Referral.STATUS_PENDING,
            kind=fqhc_reftype,
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )
        referral2.location.add(fhc)

        followup_request2 = FollowupRequest.objects.create(
            referral=referral2,
            contact_instructions="Call him",
            due_date=now().date(),
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )

        # Check that patient detail properly renders
        url = reverse('patient-detail', args=(self.pt.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check patient status -- there is one action item and followup
        # request 1 day past due and one action item and followup
        # request due today
        expected_status = "Action items 0, 1, 1, 0 days past due"
        self.assertContains(response, expected_status)

        expected_fqhc_status = Referral.STATUS_PENDING
        self.assertContains(response, expected_fqhc_status)

        # Check that referral list contains description of both referrals
        self.assertContains(response, referral1)
        self.assertContains(response, referral2)

        # Verify that the correct amount of action items are present
        total_action_items = "Action Items (6 Total)"
        self.assertContains(response, total_action_items)
        # Sanity check
        incorrect_total_action_items = "Action Items (5 Total)"
        self.assertNotContains(response, incorrect_total_action_items)

        # Now complete followup request and see if page is properly updated
        successful_res = ContactResult.objects.create(
            name="Communicated health data with patient", patient_reached=True)

        # Complete followup request for first referral
        form_data = {
            'contact_method': self.contact_method,
            'contact_status': successful_res,
            'has_appointment': PatientContact.PTSHOW_YES,
            'appointment_location': [self.refloc.pk],
            'pt_showed': PatientContact.PTSHOW_YES,
            PatientContactForm.SUCCESSFUL_REFERRAL: True
        }

        # Check that form is valid
        form = PatientContactForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        # Verify that PatientContactForm has been submitted
        url = reverse('new-patient-contact', args=(self.pt.id,
                                                   referral1.id,
                                                   followup_request1.id))
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)

        # Finally check if the new patient detail page is updated
        url = reverse('patient-detail', args=(self.pt.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        expected_status = "Action items 0, 1, 0 days past due"
        self.assertContains(response, expected_status)

        # Verify that the correct amount of action items are present
        total_action_items = "Action Items (6 Total)"
        self.assertContains(response, total_action_items)

        # Verify that the followup total has been updated
        expected_followups = "Followups (1)"
        self.assertContains(response, expected_followups)

        # There should now be 2 completed action items
        finished_action_items = "Completed Action Items (2)"
        self.assertContains(response, finished_action_items)

        # Verify that the template contains expected PatientContact description
        self.assertContains(response,
                            PatientContact.objects.first().short_text())
