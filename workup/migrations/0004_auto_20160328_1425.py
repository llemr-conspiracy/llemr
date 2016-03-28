# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0003_auto_20160122_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalworkup',
            name='height',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='weight',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='workup',
            name='height',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='workup',
            name='weight',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
