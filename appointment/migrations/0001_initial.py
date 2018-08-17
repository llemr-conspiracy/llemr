# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pttrack', '0004_auto_20171016_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('clindate', models.DateField(verbose_name=b'Appointment Date')),
                ('clintime', models.TimeField(default=datetime.datetime(2018, 8, 17, 9, 0, 0, 837487, tzinfo=utc), verbose_name=b'Time of Appointment')),
                ('appointment_type', models.CharField(default=b'CHRONIC_CARE', max_length=15, verbose_name=b'Appointment Type', choices=[(b'PSYCH_NIGHT', b'Psych Night'), (b'ACUTE_FOLLOWUP', b'Acute Followup'), (b'CHRONIC_CARE', b'Chronic Care')])),
                ('comment', models.TextField(help_text=b'What should happen at this appointment?')),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalAppointment',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('clindate', models.DateField(verbose_name=b'Appointment Date')),
                ('clintime', models.TimeField(default=datetime.datetime(2018, 8, 17, 9, 0, 0, 837487, tzinfo=utc), verbose_name=b'Time of Appointment')),
                ('appointment_type', models.CharField(default=b'CHRONIC_CARE', max_length=15, verbose_name=b'Appointment Type', choices=[(b'PSYCH_NIGHT', b'Psych Night'), (b'ACUTE_FOLLOWUP', b'Acute Followup'), (b'CHRONIC_CARE', b'Chronic Care')])),
                ('comment', models.TextField(help_text=b'What should happen at this appointment?')),
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
                'verbose_name': 'historical appointment',
            },
        ),
    ]
