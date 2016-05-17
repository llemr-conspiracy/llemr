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

    def test_last_name_correctly_lists_patients(self):
        url = reverse("pt_list_api")
        data = {'sort':'last_name'}
        response = self.client.get(url, data, format='json', follow=True) #its going to login
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.redirect_chain, [('test',302)])
        pt1 = models.Patient.objects.get(pk=1)
        
        # # we need > 1 pt, because one will have an active AI and one won't
        # pt2 = models.Patient.objects.create(
        #     first_name="Juggie",
        #     last_name="Brodeltein",
        #     middle_name="Bayer",
        #     phone='+49 178 236 5288',
        #     gender=models.Gender.objects.all()[1],
        #     address='Schulstrasse 9',
        #     city='Munich',
        #     state='BA',
        #     zip_code='63108',
        #     pcp_preferred_zip='63018',
        #     date_of_birth=datetime.date(1990, 01, 01),
        #     patient_comfortable_with_english=False,
        #     preferred_contact_method=models.ContactMethod.objects.all()[0],
        # )

        # pt3 = models.Patient.objects.create(
        #     first_name="asdf",
        #     last_name="lkjh",
        #     middle_name="Bayer",
        #     phone='+49 178 236 5288',
        #     gender=models.Gender.objects.all()[0],
        #     address='Schulstrasse 9',
        #     city='Munich',
        #     state='BA',
        #     zip_code='63108',
        #     pcp_preferred_zip='63018',
        #     date_of_birth=datetime.date(1990, 01, 01),
        #     patient_comfortable_with_english=False,
        #     preferred_contact_method=models.ContactMethod.objects.all()[0],
        # )

        # # make pt1 have and AI due tomorrow
        # pt1_ai = models.ActionItem.objects.create(
        #     author=models.Provider.objects.all()[0],
        #     author_type=models.ProviderType.objects.all()[0],
        #     instruction=models.ActionInstruction.objects.all()[0],
        #     due_date=now().date()+datetime.timedelta(days=1),
        #     comments="",
        #     patient=pt1)

        # # make pt2 have an AI due yesterday
        # pt2_ai = models.ActionItem.objects.create(
        #     author=models.Provider.objects.all()[0],
        #     author_type=models.ProviderType.objects.all()[0],
        #     instruction=models.ActionInstruction.objects.all()[0],
        #     due_date=now().date()-datetime.timedelta(days=1),
        #     comments="",
        #     patient=pt2)

        # # make pt3 have an AI that's done
        # pt3_ai = models.ActionItem.objects.create(
        #     author=models.Provider.objects.all()[0],
        #     author_type=models.ProviderType.objects.all()[0],
        #     instruction=models.ActionInstruction.objects.all()[0],
        #     due_date=now().date()-datetime.timedelta(days=15),
        #     comments="",
        #     patient=pt3)

        # self.assertEqual(response.data, {'id': 1, 'last_name': 'lauren'})
        self.assertEqual(response.data[0]['id'], 1)






