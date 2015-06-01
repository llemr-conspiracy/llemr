# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patient',
            old_name='gender',
            new_name='gender_code',
        ),
        migrations.RenameField(
            model_name='provider',
            old_name='gender',
            new_name='gender_code',
        ),
    ]
