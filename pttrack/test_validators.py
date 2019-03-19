import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from . import validators


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

    def test_validate_name(self):
        '''
        Test validator names. Name should not start or end with a space or tab
        '''

        self.assertEqual(validators.validate_name("Name"), None)
        self.assertEqual(validators.validate_name("My Name"), None) #contains ' '
        self.assertEqual(validators.validate_name("Your Name"), None) #contains \t

        with self.assertRaises(ValidationError):
            validators.validate_name(" Name") # with ' ' (space)
        with self.assertRaises(ValidationError):
            validators.validate_name("Name ")
        with self.assertRaises(ValidationError):
            validators.validate_name("Name  ")
        with self.assertRaises(ValidationError):
            validators.validate_name(" Name ")
        with self.assertRaises(ValidationError):
            validators.validate_name("  Name") # with \t (tab)
        with self.assertRaises(ValidationError):
            validators.validate_name("Name  ")
        with self.assertRaises(ValidationError):
            validators.validate_name("Name      ")
        with self.assertRaises(ValidationError):
            validators.validate_name("  Name  ")
        with self.assertRaises(ValidationError):
            validators.validate_name("  Name ") # tab then space
        with self.assertRaises(ValidationError):
            validators.validate_name(" Name  ") # space then tab
