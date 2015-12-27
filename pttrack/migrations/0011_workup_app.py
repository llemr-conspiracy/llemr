# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

#based on https://stackoverflow.com/questions/25648393

class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0001_0010_initial'),
    ]

    database_operations = [
        migrations.AlterModelTable('ClinicDate',
                                   'workup_clinicdate'),
        migrations.AlterModelTable('ClinicType',
                                   'workup_clinictype'),
        migrations.AlterModelTable('DiagnosisType',
                                   'workup_diagnosistype'),
        migrations.AlterModelTable('HistoricalWorkup',
                                   'workup_historicalworkup'),
        migrations.AlterModelTable('Workup',
                                   'workup_workup'),
        migrations.AlterModelTable('Workup.referral_location',
                                   'workup_workup_referral_location'),

        migrations.AlterField(
            model_name="Workup",
            name='referral_type',
            through='workup_workup_referral_type'),
        migrations.AlterField(
            model_name="Workup",
            name='referral_location',
            through='workup_workup_referral_location'),
        migrations.AlterField(
            model_name="Workup",
            name='diagnosis_categories',
            through='workup_workup_diagnosis_categories'),
    ]

    state_operations = [
        migrations.DeleteModel(
            name='ClinicDate',
        ),
        migrations.DeleteModel(
            name='ClinicType',
        ),
        migrations.DeleteModel(
            name='DiagnosisType',
        ),
        migrations.DeleteModel(
            name='HistoricalWorkup',
        ),
        migrations.DeleteModel(
            name='Workup',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]

