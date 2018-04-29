# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='clindate',
            field=models.DateField(verbose_name=b'Appointment Date'),
        ),
        migrations.AlterField(
            model_name='historicalappointment',
            name='clindate',
            field=models.DateField(default=datetime.datetime(2018, 4, 29, 22, 36, 34, 633639, tzinfo=utc), verbose_name=b'Appointment Date'),
            preserve_default=False,
        ),
    ]
