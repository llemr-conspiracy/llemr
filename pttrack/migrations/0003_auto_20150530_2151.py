# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0002_auto_20150530_2020'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patient',
            old_name='dob',
            new_name='date_of_birth',
        ),
    ]
