# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('demographics', '0001_initial'),
        ('pttrack', '0003_auto_20160119_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpatient',
            name='demographics',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='demographics.Demographics', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='demographics',
            field=models.OneToOneField(null=True, to='demographics.Demographics'),
        ),
    ]
