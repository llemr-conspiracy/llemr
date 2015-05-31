# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='middle_name',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
