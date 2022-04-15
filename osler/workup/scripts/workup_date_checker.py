"""
Script that identifies all workups whose encounter date differs from the written_datetime by more than 7 days 
and for each of these workups print the patient name, author name, the written_datetime, and the encounter date

Instructions for running this script are located in (PUT THE PLACE THAT I PUT THE DOC FILE IN) [note: I need to make docs for this]
"""

from osler.workup.models import Workup
from datetime import datetime

NAME = 'django.core.management.commands.shell'

def days_between(d1, d2):
    '''computes number of days between two date objects'''
    delta = d2 - d1
    return abs(delta.days)


def get_returned_workups(n):
    '''check if written_date differs from encounter_date by more than n days for each workup'''
    all_workups = Workup.objects.all()
    returned_workups = []
    for workup in all_workups:
        if days_between(workup.encounter.clinic_day, datetime.date(workup.written_datetime)) >= n:
            returned_workups.append(workup)
    return returned_workups


def print_returned_workups(returned_workups):
    '''for each workup in returned_workups, print the patient name, author name, written_datetime, and the encounter date'''
    print("All workups whose encounter date differs from the written_datetime by more than 7 days: ")
    for i, workup in enumerate(returned_workups):
        st1 = f"Workup {i} | Patient name: {workup.patient.name()}, Author name: {workup.signer}, Date "
        st2 = f"written: {datetime.date(workup.written_datetime)}, Encounter date: {workup.encounter.clinic_day}"
        print(st1 + st2)


def out_of_date_workup_finder():
    returned_workups = get_returned_workups(7)
    print_returned_workups(returned_workups)
    return returned_workups


if __name__ == NAME:
    out_of_date_workup_finder()