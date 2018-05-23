# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0002_auto_20180429_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='appointmentType',
            field=models.CharField(default=b'CHRONIC_CARE', max_length=15, verbose_name=b'Appointment Type', choices=[(b'PSYCH_NIGHT', b'Psych Night'), (b'ACUTE_FOLLOWUP', b'Acute Followup'), (b'CHRONIC_CARE', b'Chronic Care')]),
        ),
        migrations.AddField(
            model_name='appointment',
            name='clintime',
            field=models.TimeField(default=datetime.time(9, 0), verbose_name=b'Time of Appointment'),
        ),
        migrations.AddField(
            model_name='historicalappointment',
            name='appointmentType',
            field=models.CharField(default=b'CHRONIC_CARE', max_length=15, verbose_name=b'Appointment Type', choices=[(b'PSYCH_NIGHT', b'Psych Night'), (b'ACUTE_FOLLOWUP', b'Acute Followup'), (b'CHRONIC_CARE', b'Chronic Care')]),
        ),
        migrations.AddField(
            model_name='historicalappointment',
            name='clintime',
            field=models.TimeField(default=datetime.time(9, 0), verbose_name=b'Time of Appointment'),
        ),
    ]
