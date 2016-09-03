# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0006_rm_ssn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpatient',
            name='needs_workup',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='needs_workup',
            field=models.BooleanField(default=True),
        ),
    ]
