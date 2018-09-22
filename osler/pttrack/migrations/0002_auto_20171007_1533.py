# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0001_squashed_0010_auto_20170623_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionitem',
            name='priority',
            field=models.BooleanField(default=False, help_text=b'Check this box if this action item is high priority'),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='priority',
            field=models.BooleanField(default=False, help_text=b'Check this box if this action item is high priority'),
        ),
    ]
