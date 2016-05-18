import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files import File
from rest_framework.test import APITestCase

# For live tests.
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

from pttrack import models
from workup import models as workupModels
# from pttrack.test_views import build_provider, log_in_provider # runs faster if you just past the code here

# pylint: disable=invalid-name
# Whatever, whatever. I name them what I want.

BASIC_FIXTURE = 'pttrack.json' # this needs to be pttrack, else gender list goes out of bounds
# BASIC_FIXTURE = 'api.json'

# These defs can be imported as above, but runs faster if pasted here
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

class APITest(APITestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider(["Coordinator"]))

    def test_api_correctly_lists_patients(self):
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

        # # Give pt2 a workup, arbitrary date. Need to understand fixtures. Currently ClinicDate.objects is empty.
        # wu = workupModels.Workup.objects.create(
        #         clinic_day=workupModels.ClinicDate.objects.all()[0],
        #         chief_complaint="SOB",
        #         diagnosis="MI",
        #         HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
        #         ros="", pe="", A_and_P="",
        #         author=models.Provider.objects.all()[0],
        #         author_type=ProviderType.objects.all()[0],
        #         patient=pt2)

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

        # pt4 has no AI

        url = reverse("pt_list_api")

        # test last_name ordering
        # Should order by pt.history.last().history_date.date() if present, else latestwu.clinic_day.clinic_date
        data = {'sort':'last_name'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(response.data[0]['last_name'],response.data[1]['last_name'])
        self.assertLessEqual(response.data[1]['last_name'],response.data[2]['last_name'])

        # Test workup/intake ordering. Issues with making a workup, needs things contained in workup.json fixture
        # Need to understand fixtures and how to write them.
        # data = {'sort':'latest_workup'}
        # response = self.client.get(url, data, format='json')
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.data[0]['id'], pt2.id) # Hardcode the correct ordering for lack of a better idea
        # self.assertEqual(response.data[1]['id'], pt3.id)
        # self.assertEqual(response.data[2]['id'], pt1.id)

        # Write a similar test for unsigned_workup

        # Test displaying active patients
        # Need to figure how to make a patient inactive (i.e. set needs_workup to False)
        # data = {'filter':'active'}
        # response = self.client.get(url, data, format='json')
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(response.data), 2)

        # Test displaying patients with active action items (active means not due in the future?)
        data = {'filter':'ai_active'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2) #pt2, pt3 should be present since pt 1 is not past due    

        data = {'filter':'ai_inactive'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], pt1.id)

        pt3_ai.mark_done(models.Provider.objects.all()[0])
        pt3_ai.save()

        data = {'filter':'ai_active'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200) # Not sure if I should keep repeating this line
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], pt2.id)

        data = {'filter':'ai_inactive'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1) # Should still only have pt1
        self.assertEqual(response.data[0]['id'], pt1.id)
