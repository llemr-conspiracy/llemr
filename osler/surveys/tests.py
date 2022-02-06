from django.http import request
from django.test import TestCase, Client
from django.urls import reverse
from osler.core.models import Patient, Encounter, EncounterStatus, default_active_status
from osler.surveys.models import Survey, Response
from osler.core.tests.test_views import log_in_user, build_user
from osler.users.tests import factories as user_factories

import datetime


class SurveyTests(TestCase):

    fixtures = ['core']

    def setUp(self):
        self.attending = build_user([user_factories.AttendingGroupFactory])
        Survey.objects.create(title="New Survey", description="a new survey")

    def test_get_incomplete_survey_works_on_new_patient(self):
        patient = Patient.objects.get(pk=1)
        self.assertIs(len(Survey.objects.incomplete(patient.id)), 1)

    def test_get_incomplete_survey_after_filing_survey(self):
        patient = Patient.objects.get(pk=1)

        survey = Survey.objects.first()
        response = Response(survey=survey)
        response.encounter = Encounter.objects.create(
            patient=patient, clinic_day=datetime.date.today(), status=default_active_status()
        )
        response.author = self.attending
        response.author_role = self.attending.groups.first()
        response.save()

        self.assertIs(len(Survey.objects.incomplete(patient.id)), 0)

    def test_surveying_inactive_patient(self):
        client = Client()
        client.force_login(self.attending)

        survey = Survey.objects.first()
        patient = Patient.objects.get(pk=1)

        response = client.post(reverse('surveys:fill', args=[patient.id, survey.id]), {}, follow=True)
        self.assertContains(response, "inactive", status_code=400)
