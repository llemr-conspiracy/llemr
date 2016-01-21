# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0006_auto_20160121_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpatient',
            name='dependents',
            field=models.PositiveSmallIntegerField(null=True, verbose_name=b'Number of Dependents', blank=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='dependents',
            field=models.PositiveSmallIntegerField(null=True, verbose_name=b'Number of Dependents', blank=True),
        ),
    ]
