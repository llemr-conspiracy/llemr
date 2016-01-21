# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0004_auto_20160120_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpatient',
            name='dependents',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='patient',
            name='dependents',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
