# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='providertype',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.RenameField(
            model_name='providertype',
            old_name='is_staff',
            new_name='staff_view',
        ),
        migrations.AlterField(
            model_name='actionitem',
            name='comments',
            field=models.TextField(max_length=300),
        ),
        migrations.AlterField(
            model_name='historicalactionitem',
            name='comments',
            field=models.TextField(max_length=300),
        ),
    ]
