# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pttrack.validators
import workup.validators
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    replaces = [
        ('workup', '0002_add_verbose_names'),
        ('workup', '0003_auto_20160122_1631'),
        ('workup', '0004_auto_20160328_1425'),
        ('workup', '0005_auto_20160826_0620'),
        ('workup', '0007_auto_20170502_1107'),
        ('workup', '0008_auto_20170623_1048'),
        ('workup', '0009_vitals_to_numeric_type'),
        ('workup', '0010_decimal_fields_and_validation'),
        ('workup', '0011_historicalprogressnote_progressnote')]

    dependencies = [
        ('pttrack', '0001_squashed_0010_auto_20170623_1300'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClinicDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('clinic_date', models.DateField()),
                ('gcal_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ClinicType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DiagnosisType',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
        ),
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
                ('fam_hx', models.TextField(verbose_name=b'Family History')),
                ('soc_hx', models.TextField(verbose_name=b'Social History')),
                ('ros', models.TextField(verbose_name=b'ROS')),
                ('hr', models.PositiveSmallIntegerField(null=True, verbose_name=b'Heart Rate', blank=True)),
                ('bp_sys', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Systolic', validators=[workup.validators.validate_bp_systolic])),
                ('bp_dia', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Diastolic', validators=[workup.validators.validate_bp_diastolic])),
                ('rr', models.PositiveSmallIntegerField(null=True, verbose_name=b'Respiratory Rate', blank=True)),
                ('t', models.DecimalField(null=True, verbose_name=b'Temperature', max_digits=4, decimal_places=1, blank=True)),
                ('height', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('weight', models.DecimalField(null=True, max_digits=5, decimal_places=1, blank=True)),
                ('pe', models.TextField(verbose_name=b'Physical Examination')),
                ('labs_ordered_quest', models.TextField(null=True, verbose_name=b'Labs Ordered from Quest', blank=True)),
                ('labs_ordered_internal', models.TextField(null=True, verbose_name=b'Labs Ordered Internally', blank=True)),
                ('rx', models.TextField(null=True, verbose_name=b'Prescription Orders', blank=True)),
                ('got_voucher', models.BooleanField(default=False)),
                ('voucher_amount', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('patient_pays', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('got_imaging_voucher', models.BooleanField(default=False)),
                ('imaging_voucher_amount', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('patient_pays_imaging', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('will_return', models.BooleanField(default=False, help_text=b'Will the pt. return to SNHC?')),
                ('A_and_P', models.TextField()),
                ('signed_date', models.DateTimeField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('attending', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True)),
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
                ('fam_hx', models.TextField(verbose_name=b'Family History')),
                ('soc_hx', models.TextField(verbose_name=b'Social History')),
                ('ros', models.TextField(verbose_name=b'ROS')),
                ('hr', models.PositiveSmallIntegerField(null=True, verbose_name=b'Heart Rate', blank=True)),
                ('bp_sys', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Systolic', validators=[workup.validators.validate_bp_systolic])),
                ('bp_dia', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Diastolic', validators=[workup.validators.validate_bp_diastolic])),
                ('rr', models.PositiveSmallIntegerField(null=True, verbose_name=b'Respiratory Rate', blank=True)),
                ('t', models.DecimalField(null=True, verbose_name=b'Temperature', max_digits=4, decimal_places=1, blank=True)),
                ('height', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('weight', models.DecimalField(null=True, max_digits=5, decimal_places=1, blank=True)),
                ('pe', models.TextField(verbose_name=b'Physical Examination')),
                ('labs_ordered_quest', models.TextField(null=True, verbose_name=b'Labs Ordered from Quest', blank=True)),
                ('labs_ordered_internal', models.TextField(null=True, verbose_name=b'Labs Ordered Internally', blank=True)),
                ('rx', models.TextField(null=True, verbose_name=b'Prescription Orders', blank=True)),
                ('got_voucher', models.BooleanField(default=False)),
                ('voucher_amount', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('patient_pays', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('got_imaging_voucher', models.BooleanField(default=False)),
                ('imaging_voucher_amount', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('patient_pays_imaging', models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('will_return', models.BooleanField(default=False, help_text=b'Will the pt. return to SNHC?')),
                ('A_and_P', models.TextField()),
                ('signed_date', models.DateTimeField(null=True, blank=True)),
                ('attending', models.ForeignKey(related_name='attending_physician', validators=[pttrack.validators.validate_attending], to='pttrack.Provider', blank=True, help_text=b'Which attending saw the patient?', null=True)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('clinic_day', models.ForeignKey(to='workup.ClinicDate')),
                ('diagnosis_categories', models.ManyToManyField(to='workup.DiagnosisType')),
                ('other_volunteer', models.ManyToManyField(help_text=b'Which other volunteer(s) did you work with (if any)?', related_name='other_volunteer', to='pttrack.Provider', blank=True)),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
                ('referral_location', models.ManyToManyField(to='pttrack.ReferralLocation', blank=True)),
                ('referral_type', models.ManyToManyField(to='pttrack.ReferralType', blank=True)),
                ('signer', models.ForeignKey(related_name='signed_workups', validators=[pttrack.validators.validate_attending], to='pttrack.Provider', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='clinicdate',
            name='clinic_type',
            field=models.ForeignKey(to='workup.ClinicType'),
        ),
    ]
