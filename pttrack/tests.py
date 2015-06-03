from django.test import TestCase
from models import validate_zip
from django.core.exceptions import ValidationError


class CustomFuncTesting(TestCase):
    def test_validate_zip(self):
        self.assertEqual(validate_zip(12345),None)
        with self.assertRaises(ValidationError):
            validate_zip(123456)
        with self.assertRaises(ValidationError):
            validate_zip('ABCDE')
            
    def test_forms(self):
        response = self.client.post('pttrack/intake.html', {'something':'something'})
        self.assertFormError(response, 'PatientForm', 'something', 'This field is required.')