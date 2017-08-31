# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pttrack', '0010_auto_20170623_1300'),
        ('workup', '0010_decimal_fields_and_validation'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalProgressNote',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
                ('author_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical progress note',
            },
        ),
        migrations.CreateModel(
            name='ProgressNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
