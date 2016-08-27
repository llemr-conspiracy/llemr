# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import workup.validators


class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0004_auto_20160328_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalworkup',
            name='bp',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_bp]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='height',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_height]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='hr',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_hr]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='rr',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_rr]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='t',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_t]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='weight',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_weight]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='bp',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_bp]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='height',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_height]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='hr',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_hr]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='rr',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_rr]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='t',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_t]),
        ),
        migrations.AlterField(
            model_name='workup',
            name='weight',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[workup.validators.validate_weight]),
        ),
    ]
