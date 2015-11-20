# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0004_auto_20150911_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactresult',
            name='attempt_again',
            field=models.BooleanField(default=False, help_text=b'True if outcome means the pt should be contacted again.'),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='country',
            field=models.CharField(default=b'USA', max_length=100),
        ),
        migrations.AddField(
            model_name='patient',
            name='country',
            field=models.CharField(default=b'USA', max_length=100),
        ),
    ]
