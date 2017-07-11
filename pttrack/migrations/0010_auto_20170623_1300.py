# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0009_auto_20170502_1103'),
    ]

    operations = [
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='outcome',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Outcome', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='outcome',
            field=models.ForeignKey(default='NA', to='pttrack.Outcome', blank=True, null=True),
            preserve_default=False,
        ),
    ]
