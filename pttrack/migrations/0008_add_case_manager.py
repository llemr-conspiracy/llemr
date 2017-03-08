# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0007_needs_workup_default_true'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpatient',
            name='case_manager',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='case_manager',
            field=models.ForeignKey(blank=True, to='pttrack.Provider', null=True),
        ),
    ]
