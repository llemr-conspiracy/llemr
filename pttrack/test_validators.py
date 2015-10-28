from django.test import TestCase
from . import models
from django.core.exceptions import ValidationError

class CustomFuncTesting(TestCase):
    def test_validate_zip(self):
        self.assertEqual(models.validate_zip(12345), None)
        with self.assertRaises(ValidationError):
            models.validate_zip(123456)
        with self.assertRaises(ValidationError):
            models.validate_zip('ABCDE')

    def test_validate_ssn(self):
        self.assertEqual(models.validate_ssn("123-45-6789"), None)
        self.assertEqual(models.validate_ssn("123456789"), None)

        with self.assertRaises(ValidationError):
            models.validate_ssn("000-aa-0000")
        with self.assertRaises(ValidationError):
            models.validate_ssn("000-00-00000")
        with self.assertRaises(ValidationError):
            models.validate_ssn("000-000-000")
        with self.assertRaises(ValidationError):
            models.validate_ssn("1234567890")
        with self.assertRaises(ValidationError):
            models.validate_ssn('-123456789')
        with self.assertRaises(ValidationError):
            models.validate_ssn('-12345678')

