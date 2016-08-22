import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files import File

# For live tests.
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from . import models
from workup import models as workupModels
import json

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


def build_provider(roles=None, username=None, password='password'):

    # TODO this is not preferred. Should swap None for '__all__'
    # this will require hunting down all the places this is called, though.
    if roles is None:
        roles = ["Coordinator", "Attending", "Clinical", "Preclinical"]

    provtypes = [models.ProviderType.objects.get(short_name=role)
                 for role in roles]

    if username is None:
        username = 'user'+str(User.objects.all().count())

    user = User.objects.create_user(
        username,
        'tommyljones@gmail.com', password)
    user.save()

    g = models.Gender.objects.all()[0]
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
    session['clintype_pk'] = user.provider.clinical_roles.all()[0].pk
    session.save()

    return user.provider


def live_submit_login(selenium, username, password):
    username_input = selenium.find_element_by_name("username")
    username_input.send_keys(username)
    password_input = selenium.find_element_by_name("password")
    password_input.send_keys(password)
    selenium.find_element_by_xpath('//button[@type="submit"]').click()


def get_url_pt_list_identifiers(self, url):
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

    list_identifiers = []
    pt_lists = json.loads(response.context['lists'])
    for pt_list in pt_lists:
        list_identifiers.append(pt_list['identifier'])
    return list_identifiers


class LiveTesting(StaticLiveServerTestCase):
    fixtures = [BASIC_FIXTURE]

    @classmethod
    def setUpClass(cls):
        super(LiveTesting, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LiveTesting, cls).tearDownClass()

    def test_login(self):
        '''
        Test the login sequence for one clinical role and mulitiple clinical
        roles.
        '''

        build_provider(username='jrporter', password='password')

        # any valid URL should redirect to login at this point.
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        live_submit_login(self.selenium, 'jrporter', 'password')

        # now we should have to choose a clinical role
        self.assertEquals(self.selenium.current_url,
                          '%s%s%s' % (self.live_server_url,
                                      reverse('choose-clintype'),
                                      '?next='+reverse('home')))

        self.selenium.find_element_by_xpath(
            '//input[@value="Coordinator"]').click()
        self.selenium.find_element_by_xpath(
            '//button[@type="submit"]').click()

        self.assertEquals(self.selenium.current_url,
                          '%s%s' % (self.live_server_url,
                                    reverse('home')))

        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('logout')))

        # make a provider with only one role.
        build_provider(username='timmy', password='password',
                       roles=["Attending"])

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        live_submit_login(self.selenium, 'timmy', 'password')

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
        live_submit_login(self.selenium, 'timmy', 'password')

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

            jumbotron_elements = self.selenium.find_elements_by_xpath(
                '//div[@class="jumbotron"]')
            self.assertNotEqual(
                len(jumbotron_elements), 0,
                msg=" ".join(["Expected the URL ", url.name,
                              " to have a jumbotron element."]))

    def test_pt_create_js(self):
        '''
        Test the use of the new patient form. In particular, make sure that
        the SSN javascript is working.
        '''

        # build a provider and log in.
        build_provider(username='timmy', password='password',
                       roles=["Attending"])
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        live_submit_login(self.selenium, 'timmy', 'password')

        self.selenium.get('%s%s' % (self.live_server_url, reverse('intake')))

        # because we're entering data manually, we separate into stuff that
        # can be entered with sendkeys and stuff that has to be clicked.
        pt_str_data = {
            "first_name": "Juggie",
            "last_name": "Brodeltein",
            "middle_name": "Bayer",
            "address": 'Schulstrasse 9',
            "city": 'Munich',
            "state": 'BA',
            "zip_code": '63108',
            "date_of_birth": "1990-01-01",
            "ssn": '012010123'
        }

        pt_to_click = [
            "id_languages_1",
            "id_ethnicities_1",
            ]

        # select dropdown-type elements
        Select(self.selenium.find_element_by_name(
            'gender')).select_by_index(1)
        Select(self.selenium.find_element_by_name(
            'preferred_contact_method')).select_by_index(1)

        # input free-text time inputs
        for name, value in pt_str_data.iteritems():
            self.selenium.find_element_by_name('ssn').click()
            self.selenium.find_element_by_name(name).send_keys(value)

        # input click-box type elements
        for html_id in pt_to_click:
            self.selenium.find_element_by_id(html_id).click()

        self.selenium.find_element_by_id("submit-id-submit").click()

        WebDriverWait(self.selenium, 60).\
            until(EC.title_contains(pt_str_data['last_name']))

        pt = models.Patient.objects.last()

        self.assertEquals(
            self.selenium.current_url,
            '%s%s' % (self.live_server_url,
                      reverse('demographics-create', args=(pt.id,))))

        in_ssn = pt_str_data['ssn']
        out_ssn = "-".join([in_ssn[0:3], in_ssn[3:5], in_ssn[5:]])
        self.assertEquals(pt.ssn, out_ssn)


class LiveTestPatientLists(StaticLiveServerTestCase):
    fixtures = [BASIC_FIXTURE]

    @classmethod
    def setUpClass(cls):
        super(LiveTestPatientLists, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LiveTestPatientLists, cls).tearDownClass()

    def setUp(self):
        # build a provider and log in
        build_provider(username='timmy', password='password', roles=["Attending"]) # create an attending to sign a workup
        build_provider(username='timmy_coordinator', password='password', roles=["Coordinator"])

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        live_submit_login(self.selenium, 'timmy_coordinator', 'password')

        workupModels.ClinicType.objects.create(name="Basic Care Clinic")
        workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.all()[0],
            clinic_date=now().date()+datetime.timedelta(days=1),
            gcal_id="tmp")
        workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.all()[0],
            clinic_date=now().date()-datetime.timedelta(days=1),
            gcal_id="tmp")
        workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.all()[0],
            clinic_date=now().date()-datetime.timedelta(days=5),
            gcal_id="tmp")
        # log_in_provider(self.client, build_provider(["Attending"]))

        pt1 = models.Patient.objects.get(pk=1)
        pt1.toggle_active_status()
        pt1.save()

        pt2 = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.all()[1],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        pt3 = models.Patient.objects.create(
            first_name="Asdf",
            last_name="Lkjh",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.all()[0],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        pt4 = models.Patient.objects.create(
            first_name="No",
            last_name="Action",
            middle_name="Item",
            phone='+12 345 678 9000',
            gender=models.Gender.objects.all()[0],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        # Give pt2 a workup one day later.
        workupModels.Workup.objects.create(
            clinic_day=workupModels.ClinicDate.objects.all()[0], # one day later
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt2)

        # Give pt3 a workup one day ago.
        workupModels.Workup.objects.create(
            clinic_day=workupModels.ClinicDate.objects.all()[1], # one day ago
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt3)


        # Give pt1 a signed workup five days ago.
        workupModels.Workup.objects.create(
            clinic_day=workupModels.ClinicDate.objects.all()[2], # five days ago
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt1,
            signer=models.Provider.objects.all().filter(
            clinical_roles=models.ProviderType.objects.all().filter(
                short_name="Attending")[0])[0])

        # make pt1 have and AI due tomorrow
        pt1_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            instruction=models.ActionInstruction.objects.all()[0],
            due_date=now().date()+datetime.timedelta(days=1),
            comments="",
            patient=pt1)

        # make pt2 have an AI due yesterday
        pt2_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            instruction=models.ActionInstruction.objects.all()[0],
            due_date=now().date()-datetime.timedelta(days=1),
            comments="",
            patient=pt2)

        # make pt3 have an AI that during the test will be marked done
        pt3_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            instruction=models.ActionInstruction.objects.all()[0],
            due_date=now().date()-datetime.timedelta(days=15),
            comments="",
            patient=pt3)

    def test_all_patients_correct_order(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                            reverse("all-patients"))) # causing a broken pipe error
        self.assertEquals(self.selenium.current_url,
                                  '%s%s' % (self.live_server_url,
                                            reverse('all-patients')))

        # unsure how to test for multiple elements/a certain number of elements
        WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "ptlast")))
        WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "ptlatest")))

        # test ordered by last name
        pt_last_tbody = self.selenium.find_element_by_xpath("//div[@id='ptlast']/table/tbody") # this line does throw an error if the id-ed element does not exist
        first_patient_name = pt_last_tbody.find_element_by_xpath(".//tr[2]/td[1]/a").get_attribute("text")
        second_patient_name = pt_last_tbody.find_element_by_xpath(".//tr[3]/td[1]/a").get_attribute("text")
        self.assertLessEqual(first_patient_name,second_patient_name)
        self.assertEqual(first_patient_name, "Action, No I.")

        # test order by latest activity
        # more difficult to test attributes, I'm just testing that the first name is correct
        pt_last_tbody = self.selenium.find_element_by_xpath("//div[@id='ptlatest']/table/tbody")
        first_patient_name = pt_last_tbody.find_element_by_xpath(".//tr[2]/td[1]/a").get_attribute("text")
        self.assertEqual(first_patient_name, "Brodeltein, Juggie B.")        

    def test_home_correct_order(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                            reverse("home")))
        self.assertEquals(self.selenium.current_url,
                                  '%s%s' % (self.live_server_url,
                                            reverse('home')))
        
        # unsure how to test for multiple elements/a certain number of elements
        WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "activeai")))
        WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "pendingai")))
        WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "unsignedwu")))
        WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.ID, "activept")))

        # test active ai
        pt_last_tbody = self.selenium.find_element_by_xpath("//div[@id='activeai']/table/tbody")
        num_activeai_table_rows = len(pt_last_tbody.find_elements_by_xpath(".//tr"))
        first_patient_name = pt_last_tbody.find_element_by_xpath(".//tr[2]/td[1]/a").get_attribute("text")
        self.assertEqual(num_activeai_table_rows, 3) # 2 patients + 1 heading   
        self.assertEqual(first_patient_name, "Brodeltein, Juggie B.")

        # test pending (inactive) ai
        pt_last_tbody = self.selenium.find_element_by_xpath("//div[@id='pendingai']/table/tbody")
        num_activeai_table_rows = len(pt_last_tbody.find_elements_by_xpath(".//tr"))
        first_patient_name = pt_last_tbody.find_element_by_xpath(".//tr[2]/td[1]/a").get_attribute("text")
        self.assertEqual(num_activeai_table_rows, 2) # 1 patient + 1 heading   
        self.assertEqual(first_patient_name, "McNath, Frankie L.")

        # test unsigned workup
        pt_last_tbody = self.selenium.find_element_by_xpath("//div[@id='unsignedwu']/table/tbody")
        num_activeai_table_rows = len(pt_last_tbody.find_elements_by_xpath(".//tr"))
        first_patient_name = pt_last_tbody.find_element_by_xpath(".//tr[2]/td[1]/a").get_attribute("text")
        self.assertEqual(num_activeai_table_rows, 3) # 2 patients + 1 heading   
        self.assertEqual(first_patient_name, "Brodeltein, Juggie B.")

        # test active patients
        pt_last_tbody = self.selenium.find_element_by_xpath("//div[@id='activept']/table/tbody")
        num_activeai_table_rows = len(pt_last_tbody.find_elements_by_xpath(".//tr"))
        first_patient_name = pt_last_tbody.find_element_by_xpath(".//tr[2]/td[1]/a").get_attribute("text")
        self.assertEqual(num_activeai_table_rows, 2) # 1 patient + 1 heading   
        self.assertEqual(first_patient_name, "McNath, Frankie L.")

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

        pt = models.Patient.objects.all()[0]

        for pt_url in pt_urls:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError as e:
                print pt_url
                print response
                raise e

        for pt_url in pt_urls_redirect:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            try:
                self.assertEqual(response.status_code, 302)
            except AssertionError as e:
                print pt_url
                print response
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
            author_type=models.ProviderType.objects.all()[0])

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
                author_type=models.ProviderType.objects.all()[0])

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
        '''Verify that, in the absence of a provider, a provider is created,
        and that it is created correctly.'''

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
            'languages': models.Language.objects.all()[0].pk,
            'gender': models.Gender.objects.all()[0].pk,
            'provider_email': "jj@wustl.edu",
            'clinical_roles': models.ProviderType.objects.all()[0].pk,
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
        self.assertEqual(get_url_pt_list_identifiers(self, url), ['activept','activeai','pendingai','unsignedwu'])

        log_in_provider(self.client, build_provider(["Attending"]))
        self.assertEqual(get_url_pt_list_identifiers(self, url), ['unsignedwu','activept'])  

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
            'languages': [models.Language.objects.all()[0]],
            'gender': models.Gender.objects.all()[0].pk,
            'address': 'Schulstrasse 9',
            'city': 'Munich',
            'state': 'BA',
            'country': 'Germany',
            'zip_code': '63108',
            'pcp_preferred_zip': '63018',
            'ssn': "123-45-6789",
            'date_of_birth': datetime.date(1990, 01, 01),
            'patient_comfortable_with_english': False,
            'ethnicities': [models.Ethnicity.objects.all()[0]],
            'preferred_contact_method':
                models.ContactMethod.objects.all()[0].pk,
        }

    def test_can_intake_pt(self):

        n_pt = len(models.Patient.objects.all())

        submitted_pt = self.valid_pt_dict

        url = reverse('intake')

        response = self.client.post(url, submitted_pt)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(models.Patient.objects.all()), n_pt + 1)

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
        pt = models.Patient.objects.all()[0]

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")
        ai = models.ActionItem.objects.create(
            instruction=ai_inst,
            due_date=datetime.datetime.today(),
            comments="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
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
        self.assertTrue(models.ActionItem.objects.all()[0].done())
        self.assertEquals(models.ActionItem.objects.all()[0].author.pk,
                          int(self.client.session['_auth_user_id']))
        self.assertNotEqual(
            models.ActionItem.objects.all()[0].written_datetime,
            models.ActionItem.objects.all()[0].last_modified)

        # submit a request to reset the ai. should redirect to pt
        ai_url = 'reset-action-item'
        prev_mod_datetime = models.ActionItem.objects.all()[0].last_modified
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(pt.id,)),
                      response.url)
        self.assertFalse(models.ActionItem.objects.all()[0].done())

        self.assertNotEqual(
            models.ActionItem.objects.all()[0].written_datetime,
            models.ActionItem.objects.all()[0].last_modified)
        self.assertNotEqual(prev_mod_datetime,
                            models.ActionItem.objects.all()[0].last_modified)

        # make sure updating the action items url works
        ai_url = 'update-action-item'
        response = self.client.get(reverse(ai_url, args=(ai.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_create_action_item(self):

        self.assertEquals(len(models.ActionItem.objects.all()), 0)

        submitted_ai = {
            "instruction": models.ActionInstruction.objects.all()[0].pk,
            "due_date": str(datetime.date.today() + datetime.timedelta(10)),
            "comments": "models.CharField(max_length=300)" # arbitrary string
            }

        url = reverse('new-action-item', kwargs={'pt_id': 1})
        response = self.client.post(url, submitted_ai)

        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(1,)), response.url)

        self.assertEquals(len(models.ActionItem.objects.all()), 1)
        new_ai = models.ActionItem.objects.all()[0]

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
        Test that the require_providers_update() method sets all needs_update
        to True
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
            'languages': models.Language.objects.all()[0].pk,
            'gender': models.Gender.objects.all()[0].pk,
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
