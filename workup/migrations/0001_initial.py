# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pttrack.validators
import django.db.models.deletion
from django.conf import settings
import workup.validators


#based on https://stackoverflow.com/questions/25648393

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pttrack', '0001_0010_initial'),
        ('followup', '0001_initial'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='ClinicDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('clinic_date', models.DateField()),
                ('gcal_id', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'workup_clinicdate',
            }
        ),
        migrations.CreateModel(
            name='ClinicType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'workup_clinictype',
            }
        ),
        migrations.CreateModel(
            name='DiagnosisType',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'workup_diagnosistype',
            }
        ),
        migrations.CreateModel(
            name='HistoricalWorkup',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('chief_complaint', models.CharField(max_length=1000, verbose_name=b'CC')),
                ('diagnosis', models.CharField(max_length=1000, verbose_name=b'Dx')),
                ('HPI', models.TextField(verbose_name=b'HPI')),
                ('PMH_PSH', models.TextField(verbose_name=b'PMH/PSH')),
                ('meds', models.TextField(verbose_name=b'Medications')),
                ('allergies', models.TextField()),
                ('fam_hx', models.TextField()),
                ('soc_hx', models.TextField()),
                ('ros', models.TextField()),
                ('hr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('bp', models.CharField(blank=True, max_length=7, null=True, validators=[workup.validators.validate_bp])),
                ('rr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('t', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
                ('pe', models.TextField(verbose_name=b'Physical Examination')),
                ('labs_ordered_quest', models.TextField(null=True, blank=True)),
                ('labs_ordered_internal', models.TextField(null=True, blank=True)),
                ('rx', models.TextField(null=True, blank=True)),
                ('got_voucher', models.BooleanField(default=False)),
                ('voucher_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('patient_pays', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('will_return', models.BooleanField(default=False, help_text=b'Will the pt. return to SNHC?')),
                ('A_and_P', models.TextField()),
                ('signed_date', models.DateTimeField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
                ('author_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True)),
                ('clinic_day', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='workup.ClinicDate', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True)),
                ('signer', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical workup',
                'db_table': 'workup_historicalworkup',
            },
        ),
        migrations.CreateModel(
            name='Workup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('chief_complaint', models.CharField(max_length=1000, verbose_name=b'CC')),
                ('diagnosis', models.CharField(max_length=1000, verbose_name=b'Dx')),
                ('HPI', models.TextField(verbose_name=b'HPI')),
                ('PMH_PSH', models.TextField(verbose_name=b'PMH/PSH')),
                ('meds', models.TextField(verbose_name=b'Medications')),
                ('allergies', models.TextField()),
                ('fam_hx', models.TextField()),
                ('soc_hx', models.TextField()),
                ('ros', models.TextField()),
                ('hr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('bp', models.CharField(blank=True, max_length=7, null=True, validators=[workup.validators.validate_bp])),
                ('rr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('t', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
                ('pe', models.TextField(verbose_name=b'Physical Examination')),
                ('labs_ordered_quest', models.TextField(null=True, blank=True)),
                ('labs_ordered_internal', models.TextField(null=True, blank=True)),
                ('rx', models.TextField(null=True, blank=True)),
                ('got_voucher', models.BooleanField(default=False)),
                ('voucher_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('patient_pays', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('will_return', models.BooleanField(default=False, help_text=b'Will the pt. return to SNHC?')),
                ('A_and_P', models.TextField()),
                ('signed_date', models.DateTimeField(null=True, blank=True)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('clinic_day', models.ForeignKey(to='workup.ClinicDate')),
                ('diagnosis_categories', models.ManyToManyField(to='workup.DiagnosisType')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
                ('referral_location', models.ManyToManyField(to='pttrack.ReferralLocation', blank=True)),
                ('referral_type', models.ManyToManyField(to='pttrack.ReferralType', blank=True)),
                ('signer', models.ForeignKey(related_name='signed_workups', validators=[pttrack.validators.validate_attending], to='pttrack.Provider', blank=True, null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'workup_workup',
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations),
    ]
