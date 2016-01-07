# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0002_providertype_is_staff'),
    ]

    operations = [
        migrations.RenameField(
            model_name='providertype',
            old_name='is_staff',
            new_name='staff_view',
        ),
    ]
