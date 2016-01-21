# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0005_auto_20160120_2348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalpatient',
            name='chronic_condition',
        ),
        migrations.RemoveField(
            model_name='historicalpatient',
            name='resource_access',
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='ER_visit_last_year',
            field=models.BooleanField(default=False, verbose_name=b'Visited ER in the past year'),
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='dependents',
            field=models.PositiveSmallIntegerField(default=0, verbose_name=b'Number of Dependents'),
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='last_date_physician_visit',
            field=models.DateField(null=True, verbose_name=b'Date Last Visited Patient', blank=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='ER_visit_last_year',
            field=models.BooleanField(default=False, verbose_name=b'Visited ER in the past year'),
        ),
        migrations.RemoveField(
            model_name='patient',
            name='chronic_condition',
        ),
        migrations.AddField(
            model_name='patient',
            name='chronic_condition',
            field=models.ManyToManyField(to='pttrack.ChronicConditions', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='dependents',
            field=models.PositiveSmallIntegerField(default=0, verbose_name=b'Number of Dependents'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='last_date_physician_visit',
            field=models.DateField(null=True, verbose_name=b'Date Last Visited Patient', blank=True),
        ),
        migrations.RemoveField(
            model_name='patient',
            name='resource_access',
        ),
        migrations.AddField(
            model_name='patient',
            name='resource_access',
            field=models.ManyToManyField(to='pttrack.ResourceAccess', null=True, verbose_name=b'Access to Resources', blank=True),
        ),
    ]
