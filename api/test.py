import datetime

from django.core.urlresolvers import reverse
from django.utils.timezone import now
from rest_framework.test import APITestCase
from rest_framework import status

from pttrack import models
from workup import models as workupModels
from pttrack.test_views import build_provider, log_in_provider

BASIC_FIXTURE = 'api.json'


class APITest(APITestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        workupModels.ClinicType.objects.create(name="Basic Care Clinic")
        workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.first(),
            clinic_date=now().date() + datetime.timedelta(days=1))
        workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.first(),
            clinic_date=now().date() - datetime.timedelta(days=1))
        workupModels.ClinicDate.objects.create(
            clinic_type=workupModels.ClinicType.objects.first(),
            clinic_date=now().date() - datetime.timedelta(days=5))

        log_in_provider(self.client, build_provider(["Attending"]))

        pt1 = models.Patient.objects.get(pk=1)

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
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.first(),
        )

        pt3 = models.Patient.objects.create(
            first_name="Asdf",
            last_name="Lkjh",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.first(),
        )

        pt4 = models.Patient.objects.create(
            first_name="No",
            last_name="Action",
            middle_name="Item",
            phone='+12 345 678 9000',
            gender=models.Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.first(),
        )

        # Give pt2 a workup one day later.
        workupModels.Workup.objects.create(
            clinic_day=workupModels.ClinicDate.objects.first(), # one day later
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=pt2)

        # Give pt3 a workup one day ago.
        workupModels.Workup.objects.create(
            clinic_day=workupModels.ClinicDate.objects.all()[1], # one day ago
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=pt3)


        # Give pt1 a signed workup five days ago.
        workupModels.Workup.objects.create(
            clinic_day=workupModels.ClinicDate.objects.all()[2], # five days ago
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=pt1,
            signer=models.Provider.objects.all().filter(
            clinical_roles=models.ProviderType.objects.all().filter(
                short_name="Attending")[0])[0])

        # make pt1 have and AI due tomorrow
        pt1_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            instruction=models.ActionInstruction.objects.first(),
            due_date=now().date()+datetime.timedelta(days=1),
            comments="",
            priority=True,
            patient=pt1)

        # make pt2 have an AI due yesterday
        pt2_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            instruction=models.ActionInstruction.objects.first(),
            due_date=now().date()-datetime.timedelta(days=1),
            comments="",
            priority=True,
            patient=pt2)

        # make pt3 have an AI that during the test will be marked done
        pt3_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            instruction=models.ActionInstruction.objects.first(),
            due_date=now().date()-datetime.timedelta(days=15),
            comments="",
            patient=pt3)

    def test_api_list_patients_by_last_name(self):

        url = reverse("pt_list_api") # Way to have this here and not repeat this line? Reverse is called in every test now

        # Test last_name ordering
        data = {'sort': 'last_name'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(response.data[0]['last_name'],
                             response.data[1]['last_name'])
        self.assertLessEqual(response.data[1]['last_name'],
                             response.data[2]['last_name'])
        self.assertLessEqual(response.data[2]['last_name'],
                             response.data[3]['last_name'])

    def test_api_list_patients_by_latest_activity(self):
        # Test workup/intake ordering.
        data = {'sort': 'latest_workup'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data[0]['latest_workup'], None) # pt2, workup date now()+1day
        self.assertEqual(response.data[1]['latest_workup'], None) # pt4, intake date now
        self.assertNotEqual(response.data[2]['latest_workup'], None) # pt3, workup date now()-1day
        self.assertNotEqual(response.data[3]['latest_workup'], None) # pt1, workup date now()-5days

        # Check that dates are correcly sorted
        self.assertGreaterEqual(
            response.data[0]['latest_workup']['clinic_day']['clinic_date'],
            response.data[1]['history']['last']['history_date'])
        self.assertGreaterEqual(
            response.data[1]['history']['last']['history_date'],
            response.data[2]['latest_workup']['clinic_day']['clinic_date'])
        self.assertGreaterEqual(
            response.data[2]['latest_workup']['clinic_day']['clinic_date'],
            response.data[3]['latest_workup']['clinic_day']['clinic_date'])

    def test_api_list_patients_with_unsigned_workup(self):
        # Test for unsigned_workup
        data = {'filter':'unsigned_workup'}
        pt2 = models.Patient.objects.get(pk=2)
        pt3 = models.Patient.objects.get(pk=3)

        response = self.client.get(reverse("pt_list_api"), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # check that only the two patients with unsigned workups are returned
        self.assertEqual(response.data[0]['id'], pt2.id)
        self.assertEqual(response.data[1]['id'], pt3.id)
        self.assertLessEqual(response.data[0]['last_name'],response.data[1]['last_name']) # check that sorting is correct

    def test_api_list_active_patients(self):
        # Test displaying active patients (needs_workup is true).
        data = {'filter':'active'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        for patient in response.data:
            self.assertEqual(patient['needs_workup'], True)
        # self.assertEqual(response.data[0]['needs_workup'], True)
        # self.assertEqual(response.data[1]['needs_workup'], True)
        self.assertLessEqual(response.data[0]['last_name'],response.data[1]['last_name']) # check that sorting is correct

    def test_api_list_patients_with_priority_action_item(self):
        #Test displaying pts with priority action items regardless of due date
        data = {'filter':'ai_priority'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) #pt1 and 2 since both have priority AI despite due date

    def test_api_list_patients_with_active_action_item(self):
        # Test displaying patients with active action items (active means not due in the future?)
        data = {'filter':'ai_active'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) #pt2, pt3 should be present since pt 1 is not past due and pt4 has no ai

    def test_api_list_patients_with_inactive_action_item(self):
        # Test displaying patients with inactive action items
        data = {'filter': 'ai_inactive'}
        pt1 = models.Patient.objects.get(pk=1)
        pt2 = models.Patient.objects.get(pk=2)
        pt3_ai = models.ActionItem.objects.get(pk=3)
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], pt1.id)

        pt3_ai.mark_done(models.Provider.objects.first())
        pt3_ai.save()

        # Test now only has pt2
        data = {'filter': 'ai_active'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], pt2.id)

        # Should be unchanged, still only have pt1
        data = {'filter': 'ai_inactive'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], pt1.id)

    def test_api_list_cases(self):

        p = log_in_provider(self.client, build_provider(["Coordinator"]))

        pt1 = models.Patient.objects.get(pk=1)

        pt1.case_managers.add(p)

        data = {'filter': 'user_cases'}
        response = self.client.get(reverse("pt_list_api"), data, format='json')

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], pt1.id)
