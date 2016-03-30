# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0002_add_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalworkup',
            name='got_imaging_voucher',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='imaging_voucher_amount',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='patient_pays_imaging',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='workup',
            name='got_imaging_voucher',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='workup',
            name='imaging_voucher_amount',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='workup',
            name='patient_pays_imaging',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
