from django.test import TestCase
from . import validators
from django.core.exceptions import ValidationError

class TestModelFieldValidators(TestCase):
    def test_validate_zip(self):
        self.assertEqual(validators.validate_zip(12345), None)
        with self.assertRaises(ValidationError):
            validators.validate_zip(123456)
        with self.assertRaises(ValidationError):
            validators.validate_zip('ABCDE')

    def test_validate_ssn(self):
        self.assertEqual(validators.validate_ssn("123-45-6789"), None)
        self.assertEqual(validators.validate_ssn("123456789"), None)

        with self.assertRaises(ValidationError):
            validators.validate_ssn("000-aa-0000")
        with self.assertRaises(ValidationError):
            validators.validate_ssn("000-00-00000")
        with self.assertRaises(ValidationError):
            validators.validate_ssn("000-000-000")
        with self.assertRaises(ValidationError):
            validators.validate_ssn("1234567890")
        with self.assertRaises(ValidationError):
            validators.validate_ssn('-123456789')
        with self.assertRaises(ValidationError):
            validators.validate_ssn('-12345678')

