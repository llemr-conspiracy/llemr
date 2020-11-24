from rest_framework.test import APIRequestFactory
from osler.workup import models as workupModels

# Using the standard RequestFactory API to create a form POST request
#factory = APIRequestFactory()
#request = factory.post('/notes/', {'title': 'new idea'})


class WorkupAPITest():

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

        pt1 = models.Patient.objects.get(pk=1)

        workupModels.Workup.objects.create(
            clinic_day=workupModels.ClinicDate.objects.first(), # one day later
            chief_complaint="SOB",
            diagnosis="MI",
            hpi="", pmh="", psh="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", a_and_p="",
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=pt2)