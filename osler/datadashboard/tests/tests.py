from django.test import TestCase
from django.urls import reverse, resolve
from osler.core.tests import factories as core_factories
from osler.datadashboard import views


class TestUrls(TestCase):
  def test_datadashboard_url(self):
      path = reverse('datadashboard:clinic-data-dashboard')
      self.assertEqual(resolve(path).view_name, 'datadashboard:clinic-data-dashboard')
      response = self.client.get(path)
      self.assertEqual(response.status_code, 302)

  def test_patientdata_json_datadashboard_url(self):
      path = reverse('datadashboard:patientdata-json-datadashboard')
      self.assertEqual(resolve(path).view_name, 'datadashboard:patientdata-json-datadashboard')
      response = self.client.get(path)
      self.assertEqual(response.status_code, 302)

  def test_context_json_datadashboard_url(self):
      path = reverse('datadashboard:context-json-datadashboard')
      self.assertEqual(resolve(path).view_name, 'datadashboard:context-json-datadashboard')
      response = self.client.get(path)
      self.assertEqual(response.status_code, 302)
