# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import workup.validators
from workup.forms import inches2cm, fahrenheit2centigrade


def fix_temps_and_heights(apps, schema_editor):
    Workup = apps.get_model('workup', 'Workup')

    for wu in Workup.objects.all():
        wu.t = fahrenheit2centigrade(wu.t)
        wu.height = inches2cm(wu.height)
        wu.save(update_fields=['t', 'height'])

    HistoricalWorkup = apps.get_model('workup', 'HistoricalWorkup')
    for wu in HistoricalWorkup.objects.all():
        wu.t = fahrenheit2centigrade(wu.t)
        wu.height = inches2cm(wu.height)
        wu.save(update_fields=['t', 'height'])


class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0008_auto_20170623_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalworkup',
            name='height',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='hr',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name=b'Heart Rate', validators=[workup.validators.validate_hr]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='rr',
            field=models.PositiveSmallIntegerField(null=True, verbose_name=b'Respiratory Rate', blank=True),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='t',
            field=models.DecimalField(null=True, verbose_name=b'Temperature', max_digits=4, decimal_places=1, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='weight',
            field=models.DecimalField(null=True, max_digits=5, decimal_places=1, blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='height',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='hr',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name=b'Heart Rate', validators=[workup.validators.validate_hr]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='rr',
            field=models.PositiveSmallIntegerField(null=True, verbose_name=b'Respiratory Rate', blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='t',
            field=models.DecimalField(null=True, verbose_name=b'Temperature', max_digits=4, decimal_places=1, blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='weight',
            field=models.DecimalField(null=True, max_digits=5, decimal_places=1, blank=True),
        ),

        migrations.RunPython(fix_temps_and_heights, reverse_code=migrations.RunPython.noop),
    ]
