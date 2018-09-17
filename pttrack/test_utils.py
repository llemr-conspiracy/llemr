from django.test import TestCase
import datetime
from . import utils
from . import models

class AllVariationsTests(TestCase):


    def test_empty_string(self):
        '''empty string should return empty list'''
        name = ''
        return_val = utils.all_variations(name)
        self.assertEqual(return_val, [])

    def test_none(self):
        '''input = None should return empty list'''
        name = None
        return_val = utils.all_variations(name)
        self.assertEqual(return_val, [])

    def test_singleton_string(self):
        '''string of length 1 should return a list consisting of just itself'''
        name = 'b'
        return_val = utils.all_variations(name)
        self.assertEqual(return_val, [name])

    def test_first_letter_is_constant(self):
        '''Every value created should start with the first letter of the input (You are less likely
            to mess up the first letter'''
        name = 'ben'
        return_val = utils.all_variations(name)
        all_good = True
        for val in return_val:
            self.assertEqual(val[0], name[0])

    def test_last_letter_changed(self):
        '''Last letter can be deleted or changed'''
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue('bek' in return_val)
        self.assertTrue('be' in return_val)

    def test_add_letter(self):
        '''Can add letter and still get proper values'''
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue('bean' in return_val)
        self.assertTrue('baen' in return_val)

    def test_remove_letter(self):
        '''letter can be removed'''
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue('bn' in return_val)

    def test_remove_letter(self):
        '''innitial name should be returned'''
        name = 'ben'
        return_val = utils.all_variations(name)
        self.assertTrue(name in return_val)

    def test_number_vals_returned(self):
        '''for each letter (other than the first letter) there should be 26 variations for
            changes in a letter, 26 for adding a letter, and 1 for removing the lette,
            and also add the original input giving a total of (len(input) - 1) * 53 + 1 changes '''
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
        'gender': models.Gender(long_name = "Male", short_name = "m"),
        'pcp_preferred_zip': '63018',
        'date_of_birth': datetime.date(1990, 01, 01),
        'patient_comfortable_with_english': False,
        'preferred_contact_method': models.ContactMethod.objects.first(),
    }
    pt1 = models.Patient.objects.create(
        first_name="Benjamin",
        last_name="Katz",
        middle_name="J",
        **pt_prototype
    )

    pt2 = models.Patient.objects.create(
        first_name="Artur",
        last_name="Meller",
        middle_name="Bayer",
        **pt_prototype
    )

    pt3 = models.Patient.objects.create(
        first_name="Arthur",
        last_name="Meller",
        middle_name="Item",
        **pt_prototype
    )

    pt4 = models.Patient.objects.create(
        first_name="Artr",
        last_name="Muller",
        middle_name="Patient",
        **pt_prototype
    )

    pt5 = models.Patient.objects.create(
        first_name="Artemis",
        last_name="Meller",
        middle_name="Patient",
        **pt_prototype
    )


class return_duplicatesTests(TestCase):

    def test_empty_first_name(self):
        '''If first and last name is empty string should return None
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("", "Katz")
        self.assertEqual(result, None)

    def test_empty_last_name(self):
        '''If last name is empty string but first is not should return None
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("Benjamin", "")
        self.assertEqual(result, None)

    def test_empty_first_last_name(self):
        '''If first name is empty string but last is not should return None
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("", "")
        self.assertEqual(result, None)

    def test_identical_first_last_name(self):
        '''If first and last name exactly match database entry, it should be returned
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamin", "katz")
        self.assertEqual(len(result), 1)

    def test_wrong_last_name(self):
        '''If first name matches but last name is completely different no results should be returned
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamin", "meller")
        self.assertEqual(len(result), 0)

    def test_wrong_first_name(self):
        '''If last name matches but first name is completely different no results should be returned
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("artur", "katz")
        self.assertEqual(len(result), 0)

    def test_first_last_off_by_1(self):
        '''If first name and last name have 1 letter difference from true value (letter added or removed)
            the database entry should still be returned
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamian", "ktz")
        self.assertEqual(len(result), 1)

    def test_start_with_first(self):
        '''If first name given matches the start of the actual name, shoud return result
        '''
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("ben", "katz")
        self.assertEqual(len(result), 1)

    def test_start_with_first_wrong_last(self):
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("ben", "katzington")
        self.assertEqual(len(result), 0)

    def test_start_with_last(self):
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("benjamin", "ka")
        self.assertEqual(len(result), 0)

    def test_return_multiple(self):
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("artur", "meller")
        self.assertEqual(len(result), 3)

    def test_return_multiple_starts_with(self):
        create_pts()
        self.assertEqual(len(models.Patient.objects.all()), 5)
        result = utils.return_duplicates("art", "meller")
        self.assertEqual(len(result), 4)







