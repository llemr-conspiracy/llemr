import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from . import validators

BASIC_FIXTURE = 'basic_fixture'

class TestModelFieldValidators(TestCase):
    def test_validate_zip(self):
        '''
        Zip codes should be only 5 digits, and contain no letters. It should
        accept numbers and strings.
        '''
        self.assertEqual(validators.validate_zip(12345), None)
        self.assertEqual(validators.validate_zip('12345'), None)

        with self.assertRaises(ValidationError):
            validators.validate_zip(123456)
        with self.assertRaises(ValidationError):
            validators.validate_zip('ABCDE')
        with self.assertRaises(ValidationError):
            validators.validate_zip('12a45')

    def test_validate_ssn(self):
        '''
        Test the social security number parser. It should accept both the
        format with hypens and the format without.
        '''
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

    def test_validate_birth_date(self):
        '''
        Test our validator for birth dates. Birth dates should be in the past
        but not farther away than 150 years.
        '''

        self.assertEqual(validators.validate_birth_date(
            now().date() - datetime.timedelta(365 * 10)), None)

        with self.assertRaises(ValidationError):
            validators.validate_birth_date(
                now().date() + datetime.timedelta(365))
        with self.assertRaises(ValidationError):
            validators.validate_birth_date(
                now().date() - datetime.timedelta(365 * 151))
