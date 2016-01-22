from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from pttrack.test_views import build_provider, log_in_provider
from pttrack.models import Patient

from . import models
from . import forms
# Create your tests here.


class ViewsExistTest(TestCase):
    '''
    Verify that views involving the wokrup are functioning.
    '''
    fixtures = ['pttrack']

    def setUp(self):

    	log_in_provider(self.client, build_provider())

        models.IncomeRange.objects.create(name="Default")
        models.EducationLevel.objects.create(name="Default")
        models.WorkStatus.objects.create(name="Default")
        models.ResourceAccess.objects.create(name="Default")
        models.ChronicCondition.objects.create(name="Default")
        models.TransportationOption.objects.create(name="Default")


    def test_url_response(self):

        dg_urls = ['demographics-detail', 'demographics-update']

        dg = models.Demographics.objects.create(
            creation_date=date.today(),
            annual_income=models.IncomeRange.objects.all()[0],
            education_level=models.EducationLevel.objects.all()[0],
            transportation=models.TransportationOption.objects.all()[0],
            work_status=models.WorkStatus.objects.all()[0],
            has_insurance=True,
            ER_visit_last_year=True,
            last_date_physician_visit=date.today(),
            lives_alone=True,
            dependents=4,
            currently_employed=True)

        dg.chronic_condition.add(models.ChronicCondition.objects.all()[0])
        dg.resource_access.add(models.ResourceAccess.objects.all()[0])
        dg.save()

        pt = Patient.objects.all()[0]
        pt.demographics = dg
        pt.save()

        dg.patient = pt
        dg.save()

        for dg_url in dg_urls:
            response = self.client.get(reverse(dg_url, args=(dg.id,)))
            self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('demographics-create', args=(pt.id,)))
        self.assertEqual(response.status_code, 200)
