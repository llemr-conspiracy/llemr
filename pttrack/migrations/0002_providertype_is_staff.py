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
    ]
