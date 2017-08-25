# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import workup.validators


class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0009_vitals_to_numeric_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalworkup',
            name='bp_dia',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Diastolic', validators=[workup.validators.validate_bp_diastolic]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='bp_sys',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Systolic', validators=[workup.validators.validate_bp_systolic]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='bp_dia',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Diastolic', validators=[workup.validators.validate_bp_diastolic]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='bp_sys',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Systolic', validators=[workup.validators.validate_bp_systolic]),
        ),
    ]
