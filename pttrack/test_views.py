import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files import File

# For live tests.
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

from .  import models

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

    if roles is None:
        roles = ["Coordinator", "Attending", "Clinical", "Preclinical"]

    if username is None:
        username = 'user'+str(User.objects.all().count())

    user = User.objects.create_user(
        username,
        'tommyljones@gmail.com', password)
    user.save()

    g = models.Gender.objects.all()[0]
    models.Provider.objects.create(
        first_name="Tommy", middle_name="Lee", last_name="Jones",
        phone="425-243-9115", gender=g, associated_user=user)

    coordinator_provider = models.ProviderType.objects.all()[2]
    coordinator_provider.staff_view = True
    coordinator_provider.save()

    for role in roles:
        try:
            ptype = models.ProviderType.objects.filter(short_name=role)[0]
        except IndexError:
            raise KeyError(
                "'"+role+"' isn't in the list of ProviderTypes: "+
                str([p.short_name for p in models.ProviderType.objects.all()]))
        user.provider.clinical_roles.add(ptype)

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

        response = self.client.get(reverse('new-provider'))
        # self.assertRedirects(response, reverse('new-provider')+'?next='+final_url)

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
            'date_of_birth': datetime.date(1990, 01, 01),
            'patient_comfortable_with_english': False,
            'ethnicities': [models.Ethnicity.objects.all()[0]],
            'preferred_contact_method':
                models.ContactMethod.objects.all()[0].pk,
        }

    def test_ssn_rewrite(self):
        '''SSNs given without hypens should be automatically hypenated.'''

        submitted_pt = self.valid_pt_dict
        submitted_pt['ssn'] = "123456789"

        response = self.client.post(reverse('intake'), submitted_pt)

        new_pt = list(models.Patient.objects.all())[-1]
        self.assertEquals(new_pt.ssn, "123-45-6789")

    def test_can_intake_pt(self):

        n_pt = len(models.Patient.objects.all())

        submitted_pt = self.valid_pt_dict

        url = reverse('intake')

        response = self.client.post(url, submitted_pt)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(models.Patient.objects.all()), n_pt + 1)

        new_pt = models.Patient.objects.all()[n_pt]
        
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

    def test_home_has_correct_patients(self):
        pt1 = models.Patient.objects.get(pk=1)

        # we need > 1 pt, because one will have an active AI and one won't
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
            first_name="asdf",
            last_name="lkjh",
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

        # make pt3 have an AI that's done
        pt3_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            instruction=models.ActionInstruction.objects.all()[0],
            due_date=now().date()-datetime.timedelta(days=15),
            comments="",
            patient=pt3)

        url = reverse("home")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        print models.ProviderType.objects.all()[2].staff_view

        #pt2, pt3 should be present since pt 1 is not past due
        self.assertEqual(len(response.context['zipped_list'][1][1]), 2)
        self.assertIn(pt2, response.context['zipped_list'][1][1])
        self.assertIn(pt3, response.context['zipped_list'][1][1])

        pt3_ai.mark_done(models.Provider.objects.all()[0])
        pt3_ai.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # now only pt2 should be present, since only pt3's AI is now done
        self.assertEqual(len(response.context['zipped_list'][1][1]), 1)
        self.assertIn(pt2, response.context['zipped_list'][1][1])


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
