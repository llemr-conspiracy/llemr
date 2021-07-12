from django.test import TestCase
from django.urls import reverse, resolve
from osler.datadashboard import views

class TestUrls(TestCase):
  def test_datadashboard_url(self):
      path = reverse('datadashboard:clinic-data-dashboard')
      self.assertEqual(resolve(path).view_name, 'datadashboard:clinic-data-dashboard')

  def test_patientdata_json_datadashboard_url(self):
      path = reverse('datadashboard:patientdata-json-datadashboard')
      self.assertEqual(resolve(path).view_name, 'datadashboard:patientdata-json-datadashboard')

  def test_context_json_datadashboard_url(self):
      path = reverse('datadashboard:context-json-datadashboard')
      self.assertEqual(resolve(path).view_name, 'datadashboard:context-json-datadashboard')
