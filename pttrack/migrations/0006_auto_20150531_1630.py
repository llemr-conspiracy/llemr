# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0005_auto_20150531_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider', blank=True),
        ),
    ]
