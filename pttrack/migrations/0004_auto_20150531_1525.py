# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0003_auto_20150530_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followup',
            name='written_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 31, 15, 25, 22, 495328)),
        ),
    ]
