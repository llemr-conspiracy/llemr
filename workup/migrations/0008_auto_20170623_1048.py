# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0010_auto_20170623_1300'),
        ('workup', '0007_auto_20170502_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalworkup',
            name='attending',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='workup',
            name='attending',
            field=models.ForeignKey(related_name='attending_physician', to='pttrack.Provider', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='workup',
            name='other_volunteer',
            field=models.ManyToManyField(related_name='other_volunteer', to='pttrack.Provider', blank=True),
        ),
    ]
