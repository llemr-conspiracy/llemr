# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_case_manager(apps, schema_editor):
    Patient = apps.get_model('pttrack','Patient')
    for patient_person in Patient.objects.all():
        try:
            if patient_person.case_manager != None:
                patient_person.case_managers.add(patient_person.case_manager)
            if patient_person.case_manager_2 != None:
                patient_person.case_managers.add(patient_person.case_manager_2)
        except AttributeError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0003_auto_20171014_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='case_managers',
            field=models.ManyToManyField(to='pttrack.Provider'),
        ),
        migrations.RunPython(move_case_manager),
        migrations.RemoveField(
            model_name='historicalpatient',
            name='case_manager',
        ),
        migrations.RemoveField(
            model_name='historicalpatient',
            name='case_manager_2',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='case_manager_2',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='case_manager',
        ),
    ]
