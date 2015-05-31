# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0004_auto_20150531_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followup',
            name='written_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
