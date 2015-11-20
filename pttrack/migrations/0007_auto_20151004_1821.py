# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0006_auto_20151002_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpatient',
            name='needs_workup',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='patient',
            name='needs_workup',
            field=models.BooleanField(default=False),
        ),
    ]
