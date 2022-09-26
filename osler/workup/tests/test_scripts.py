from django.test import TestCase
from osler.workup.models import Workup
from osler.workup.scripts import workup_date_checker
from .factories import WorkupFactory
import datetime

class testScripts(TestCase):

    fixtures = ['workup', 'core']

    def test_workup_date_checker(self):
        d1 = datetime.datetime(2019, 4, 13)
        d2 = datetime.datetime.now() - datetime.timedelta(days=2)
        d3 = datetime.datetime(2018, 4, 4)
        
        workup_one = WorkupFactory()
        workup_two = WorkupFactory()
        workup_three = WorkupFactory()

        workup_one.written_datetime = d1
        workup_two.written_datetime = d2
        workup_three.written_datetime = d3

        workup_one.save()
        workup_two.save()
        workup_three.save()

        expected_returned_workups = [workup_one, workup_three]
        assert workup_date_checker.out_of_date_workup_finder() == expected_returned_workups
        

