# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0005_auto_20160628_1852'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalpatient',
            name='ssn',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='ssn',
        ),
    ]
