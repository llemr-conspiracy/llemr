# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactResult',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('attempt_again', models.BooleanField(default=False, help_text=b'True if outcome means the pt should be contacted again.')),
                ('patient_reached', models.BooleanField(default=True, help_text=b'True if outcome means they reached the patient')),
            ],
        ),
        migrations.CreateModel(
            name='GeneralFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('contact_method', models.ForeignKey(to='pttrack.ContactMethod')),
                ('contact_resolution', models.ForeignKey(to='followup.ContactResult')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalGeneralFollowup',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
                ('author_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True)),
                ('contact_method', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True)),
                ('contact_resolution', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='followup.ContactResult', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical general followup',
            },
        ),
        migrations.CreateModel(
            name='HistoricalLabFollowup',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('communication_success', models.BooleanField(help_text=b'Were you able to communicate the results?')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
                ('author_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True)),
                ('contact_method', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True)),
                ('contact_resolution', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='followup.ContactResult', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical lab followup',
            },
        ),
        migrations.CreateModel(
            name='HistoricalReferralFollowup',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('has_appointment', models.BooleanField(help_text=b'Does the patient have an appointment?')),
                ('pt_showed', models.CharField(blank=True, max_length=7, null=True, help_text=b'Did the patient show up to the appointment?', choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Not yet', b'Not yet')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('apt_location', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ReferralLocation', null=True)),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
                ('author_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True)),
                ('contact_method', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True)),
                ('contact_resolution', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='followup.ContactResult', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical referral followup',
            },
        ),
        migrations.CreateModel(
            name='HistoricalVaccineFollowup',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('subsq_dose', models.BooleanField(verbose_name=b'Has the patient committed to coming back for another dose?')),
                ('dose_date', models.DateField(help_text=b'When does the patient want to get their next dose (if applicable)?', null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
                ('author_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True)),
                ('contact_method', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True)),
                ('contact_resolution', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='followup.ContactResult', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical vaccine followup',
            },
        ),
        migrations.CreateModel(
            name='LabFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('communication_success', models.BooleanField(help_text=b'Were you able to communicate the results?')),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('contact_method', models.ForeignKey(to='pttrack.ContactMethod')),
                ('contact_resolution', models.ForeignKey(to='followup.ContactResult')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NoAptReason',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='NoShowReason',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReferralFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('has_appointment', models.BooleanField(help_text=b'Does the patient have an appointment?')),
                ('pt_showed', models.CharField(blank=True, max_length=7, null=True, help_text=b'Did the patient show up to the appointment?', choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Not yet', b'Not yet')])),
                ('apt_location', models.ForeignKey(blank=True, to='pttrack.ReferralLocation', help_text=b'Where is the appointment?', null=True)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('contact_method', models.ForeignKey(to='pttrack.ContactMethod')),
                ('contact_resolution', models.ForeignKey(to='followup.ContactResult')),
                ('noapt_reason', models.ForeignKey(blank=True, to='followup.NoAptReason', help_text=b"If the patient didn't make an appointment, why not?", null=True)),
                ('noshow_reason', models.ForeignKey(blank=True, to='followup.NoShowReason', help_text=b"If the patient didn't go to appointment, why not?", null=True)),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
                ('referral_type', models.ForeignKey(blank=True, to='pttrack.ReferralType', help_text=b'What kind of provider was the patient referred to?', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VaccineFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('subsq_dose', models.BooleanField(verbose_name=b'Has the patient committed to coming back for another dose?')),
                ('dose_date', models.DateField(help_text=b'When does the patient want to get their next dose (if applicable)?', null=True, blank=True)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('contact_method', models.ForeignKey(to='pttrack.ContactMethod')),
                ('contact_resolution', models.ForeignKey(to='followup.ContactResult')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='noapt_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='followup.NoAptReason', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='noshow_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='followup.NoShowReason', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='referral_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ReferralType', null=True),
        ),
    ]
