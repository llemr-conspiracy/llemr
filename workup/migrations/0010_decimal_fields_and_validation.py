# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pttrack.validators
import django.core.validators
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
            model_name='historicalworkup',
            name='hr',
            field=models.PositiveSmallIntegerField(null=True, verbose_name=b'Heart Rate', blank=True),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='imaging_voucher_amount',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='patient_pays',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='patient_pays_imaging',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='voucher_amount',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='attending',
            field=models.ForeignKey(related_name='attending_physician', validators=[pttrack.validators.validate_attending], to='pttrack.Provider', blank=True, help_text=b'Which attending saw the patient?', null=True),
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
        migrations.AlterField(
            model_name='workup',
            name='hr',
            field=models.PositiveSmallIntegerField(null=True, verbose_name=b'Heart Rate', blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='imaging_voucher_amount',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='other_volunteer',
            field=models.ManyToManyField(help_text=b'Which other volunteer(s) did you work with (if any)?', related_name='other_volunteer', to='pttrack.Provider', blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='patient_pays',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='patient_pays_imaging',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='voucher_amount',
            field=models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
