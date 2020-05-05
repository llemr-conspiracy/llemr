from __future__ import unicode_literals
from django.test import TestCase
import datetime
from . import utils
from . import models


class AllVariationsTests(TestCase):
    """all_variations is a function that is used to help search for all
    variations of a string that have either added, removed, or changed
    1 letter. Function returns a list of all variations of the input string.
    """

    def test_empty_string(self):
        """empty string should return empty list"""
        name = ''
        return_val = utils.all_variations(name)
        self.assertEqual(return_val, [])

    def test_none(self):
        """input = None should return empty list"""
        name = None
        return_val = utils.all_variations(name)
        self.assertEqual(return_val, [])

    def test_singleton_string(self):
        """string of length 1 should return a list consisting of just
        itself"""
        name = 'b'
        return_val = utils.all_variations(name)
        self.assertEqual(return_val, [name])

    def test_first_letter_is_constant(self):
        """Every value created should start with the first letter of the
         search input (You are less likely to mess up the first letter
         and not realize it"""
        name = 'ben'
        return_val = utils.all_variations(name)
        for val in return_val:
            self.assertEqual(val[0], name[0])

    def test_last_letter_changed(self):
        """Last letter can be deleted or changed"""
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue('bek' in return_val)
        self.assertTrue('be' in return_val)

    def test_add_letter(self):
        """Can add letter and still get proper values"""
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue('bean' in return_val)
        self.assertTrue('baen' in return_val)

    def test_remove_letter(self):
        """letter can be removed"""
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue('bn' in return_val)

    def test_initial_name_present(self):
        """initial name should be returned"""
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue(name in return_val)

    def test_number_vals_returned(self):
        """for each letter (other than the first letter) there should be
        26 variations for changes in a letter, 26 for adding a letter,
        and 1 for removing the letter, and also add the original input
        giving a total of (len(input) - 1) * 53 + 1 changes """
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertEqual(len(return_val), (len(name) - 1) * 53 + 1)


def create_pts():
    pt_prototype = {
        'phone': '+49 178 236 5288',
        'address': 'Schulstrasse 9',
        'city': 'Munich',
        'state': 'BA',
        'zip_code': '63108',
        'gender': models.Gender(long_name="Male", short_name="m"),
        'pcp_preferred_zip': '63018',
        'date_of_birth': datetime.date(1990, 1, 1),
        'patient_comfortable_with_english': False,
        'preferred_contact_method': models.ContactMethod.objects.first(),
    }

    models.Patient.objects.create(
        first_name="Benjamin",
        last_name="Katz",
        middle_name="J",
        **pt_prototype
    )

    models.Patient.objects.create(
        first_name="Artur",
        last_name="Meller",
        middle_name="Bayer",
        **pt_prototype
    )

    models.Patient.objects.create(
        first_name="Arthur",
        last_name="Meller",
        middle_name="Item",
        **pt_prototype
    )

    models.Patient.objects.create(
        first_name="Artr",
        last_name="Muller",
        middle_name="Patient",
        **pt_prototype
    )

    models.Patient.objects.create(
        first_name="Artemis",
        last_name="Meller",
        middle_name="Patient",
        **pt_prototype
    )


class return_duplicatesTests(TestCase):
    """Search database for all variations of first and last name off by 1
    letter (except for first letter must be correct) and return matching
    results.  First name may also be abbreviated (to cover cases like
    ben and benjamin)
    """

    def tearDown(self):
        # necessary because of the ForeignKey on_delete=PROTECT directives
        models.Patient.objects.all().delete()

    def test_empty_first_name(self):
        """If first and last name is empty string should return None
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("", "Katz")
        self.assertEqual(result, None)

    def test_empty_last_name(self):
        """If last name is empty string but first is not should return None
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("Benjamin", "")
        self.assertEqual(result, None)

    def test_empty_first_last_name(self):
        """If first name is empty string but last is not should return None
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("", "")
        self.assertEqual(result, None)

    def test_identical_first_last_name(self):
        """If first and last name exactly match database entry, it
        should be returned
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamin", "katz")
        self.assertEqual(len(result), 1)

    def test_wrong_last_name(self):
        """If first name matches but last name is completely different
        no results should be returned
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamin", "meller")
        self.assertEqual(len(result), 0)

    def test_wrong_first_name(self):
        """If last name matches but first name is completely different
        no results should be returned
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("artur", "katz")
        self.assertEqual(len(result), 0)

    def test_first_last_off_by_1(self):
        """If first name and last name have 1 letter difference from
        true value (letter added or removed) the database entry should
        still be returned
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamian", "ktz")
        self.assertEqual(len(result), 1)

    def test_start_with_first(self):
        """If first name given matches the start of the actual name,
        shoud return result
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("ben", "katz")
        self.assertEqual(len(result), 1)

    def test_start_with_first_wrong_last(self):
        """If first name given matches start of the actual name
        but last name does not no results returned
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("ben", "katzington")
        self.assertEqual(len(result), 0)

    def test_start_with_last(self):
        """If last name given only matches the start of the actual name,
        no results returned (last names are never abbreviated)
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamin", "ka")
        self.assertEqual(len(result), 0)

    def test_return_multiple(self):
        """Ensure function will return all eligeble results
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("artur", "meller")
        self.assertEqual(len(result), 3)

    def test_return_multiple_starts_with(self):
        """Ensure function will return all eligeble results if first name
        only matches start of the actual names
        """
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("art", "meller")
        self.assertEqual(len(result), 4)
