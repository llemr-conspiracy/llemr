# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pttrack.validators
import pttrack.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionInstruction',
            fields=[
                ('instruction', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateField(help_text=b'MM/DD/YYYY or YYYY-MM-DD')),
                ('comments', models.CharField(max_length=300)),
                ('completion_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
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
            name='ContactMethod',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContactResult',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('attempt_again', models.BooleanField(default=False, help_text=b'True if outcome means the pt should be contacted again.')),
                ('patient_reached', models.BooleanField(default=True, help_text=b'True if the outcome means they did not reach the patient')),
            ],
        ),
        migrations.CreateModel(
            name='DiagnosisType',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('image', models.FileField(help_text=b'Please deidentify all file names before upload! Delete all files after upload!', upload_to=pttrack.models.make_filepath, verbose_name=b'PDF File or Image Upload')),
                ('comments', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ethnicity',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('long_name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('short_name', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='GeneralFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalActionItem',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('due_date', models.DateField(help_text=b'MM/DD/YYYY or YYYY-MM-DD')),
                ('comments', models.CharField(max_length=300)),
                ('completion_date', models.DateTimeField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical action item',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDocument',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('title', models.CharField(max_length=200)),
                ('image', models.TextField(help_text=b'Please deidentify all file names before upload! Delete all files after upload!', max_length=100, verbose_name=b'PDF File or Image Upload')),
                ('comments', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical document',
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
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical lab followup',
            },
        ),
        migrations.CreateModel(
            name='HistoricalPatient',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=40)),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(default=b'St. Louis', max_length=50)),
                ('state', models.CharField(default=b'MO', max_length=2)),
                ('zip_code', models.CharField(max_length=5, validators=[pttrack.validators.validate_zip])),
                ('country', models.CharField(default=b'USA', max_length=100)),
                ('pcp_preferred_zip', models.CharField(blank=True, max_length=5, null=True, validators=[pttrack.validators.validate_zip])),
                ('date_of_birth', models.DateField(validators=[pttrack.validators.validate_birth_date])),
                ('patient_comfortable_with_english', models.BooleanField(default=True)),
                ('ssn', models.CharField(blank=True, max_length=9, null=True, validators=[pttrack.validators.validate_ssn])),
                ('alternate_phone_1_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_1', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4', models.CharField(max_length=40, null=True, blank=True)),
                ('needs_workup', models.BooleanField(default=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('gender', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Gender', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('preferred_contact_method', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical patient',
            },
        ),
        migrations.CreateModel(
            name='HistoricalProvider',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=40)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('associated_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('gender', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Gender', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical provider',
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
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical vaccine followup',
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
                ('fam_hx', models.TextField()),
                ('soc_hx', models.TextField()),
                ('ros', models.TextField()),
                ('hr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('bp', models.CharField(blank=True, max_length=7, null=True, validators=[pttrack.validators.validate_bp])),
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
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical workup',
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
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
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
            name='Patient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=40)),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(default=b'St. Louis', max_length=50)),
                ('state', models.CharField(default=b'MO', max_length=2)),
                ('zip_code', models.CharField(max_length=5, validators=[pttrack.validators.validate_zip])),
                ('country', models.CharField(default=b'USA', max_length=100)),
                ('pcp_preferred_zip', models.CharField(blank=True, max_length=5, null=True, validators=[pttrack.validators.validate_zip])),
                ('date_of_birth', models.DateField(validators=[pttrack.validators.validate_birth_date])),
                ('patient_comfortable_with_english', models.BooleanField(default=True)),
                ('ssn', models.CharField(blank=True, max_length=9, null=True, validators=[pttrack.validators.validate_ssn])),
                ('alternate_phone_1_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_1', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4', models.CharField(max_length=40, null=True, blank=True)),
                ('needs_workup', models.BooleanField(default=False)),
                ('ethnicities', models.ManyToManyField(to='pttrack.Ethnicity')),
                ('gender', models.ForeignKey(to='pttrack.Gender')),
                ('languages', models.ManyToManyField(help_text=b'Specify here languages that are spoken at a level sufficient to be used for medical communication.', to='pttrack.Language')),
                ('preferred_contact_method', models.ForeignKey(blank=True, to='pttrack.ContactMethod', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=40)),
                ('associated_user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProviderType',
            fields=[
                ('long_name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('signs_charts', models.BooleanField(default=False)),
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
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReferralLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('address', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ReferralType',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
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
                ('contact_resolution', models.ForeignKey(to='pttrack.ContactResult')),
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
                ('fam_hx', models.TextField()),
                ('soc_hx', models.TextField()),
                ('ros', models.TextField()),
                ('hr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('bp', models.CharField(blank=True, max_length=7, null=True, validators=[pttrack.validators.validate_bp])),
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
                ('clinic_day', models.ForeignKey(to='pttrack.ClinicDate')),
                ('diagnosis_categories', models.ManyToManyField(to='pttrack.DiagnosisType')),
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
            model_name='referralfollowup',
            name='apt_location',
            field=models.ForeignKey(blank=True, to='pttrack.ReferralLocation', help_text=b'Where is the appointment?', null=True),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='contact_method',
            field=models.ForeignKey(to='pttrack.ContactMethod'),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='contact_resolution',
            field=models.ForeignKey(to='pttrack.ContactResult'),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='noapt_reason',
            field=models.ForeignKey(blank=True, to='pttrack.NoAptReason', help_text=b"If the patient didn't make an appointment, why not?", null=True),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='noshow_reason',
            field=models.ForeignKey(blank=True, to='pttrack.NoShowReason', help_text=b"If the patient didn't go to appointment, why not?", null=True),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='referral_type',
            field=models.ForeignKey(blank=True, to='pttrack.ReferralType', help_text=b'What kind of provider was the patient referred to?', null=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='clinical_roles',
            field=models.ManyToManyField(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='provider',
            name='gender',
            field=models.ForeignKey(to='pttrack.Gender'),
        ),
        migrations.AddField(
            model_name='provider',
            name='languages',
            field=models.ManyToManyField(help_text=b'Specify here languages that are spoken at a level sufficient to be used for medical communication.', to='pttrack.Language'),
        ),
        migrations.AddField(
            model_name='labfollowup',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='labfollowup',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='labfollowup',
            name='contact_method',
            field=models.ForeignKey(to='pttrack.ContactMethod'),
        ),
        migrations.AddField(
            model_name='labfollowup',
            name='contact_resolution',
            field=models.ForeignKey(to='pttrack.ContactResult'),
        ),
        migrations.AddField(
            model_name='labfollowup',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='clinic_day',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ClinicDate', null=True),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='signer',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalvaccinefollowup',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalvaccinefollowup',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicalvaccinefollowup',
            name='contact_method',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True),
        ),
        migrations.AddField(
            model_name='historicalvaccinefollowup',
            name='contact_resolution',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactResult', null=True),
        ),
        migrations.AddField(
            model_name='historicalvaccinefollowup',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalvaccinefollowup',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='apt_location',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ReferralLocation', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='contact_method',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='contact_resolution',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactResult', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='noapt_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.NoAptReason', null=True),
        ),
        migrations.AddField(
            model_name='historicalreferralfollowup',
            name='noshow_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.NoShowReason', null=True),
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
        migrations.AddField(
            model_name='historicallabfollowup',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicallabfollowup',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicallabfollowup',
            name='contact_method',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True),
        ),
        migrations.AddField(
            model_name='historicallabfollowup',
            name='contact_resolution',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactResult', null=True),
        ),
        migrations.AddField(
            model_name='historicallabfollowup',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicallabfollowup',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='historicalgeneralfollowup',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalgeneralfollowup',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicalgeneralfollowup',
            name='contact_method',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True),
        ),
        migrations.AddField(
            model_name='historicalgeneralfollowup',
            name='contact_resolution',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactResult', null=True),
        ),
        migrations.AddField(
            model_name='historicalgeneralfollowup',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalgeneralfollowup',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='document_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.DocumentType', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='completion_author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='instruction',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ActionInstruction', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='generalfollowup',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='generalfollowup',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='generalfollowup',
            name='contact_method',
            field=models.ForeignKey(to='pttrack.ContactMethod'),
        ),
        migrations.AddField(
            model_name='generalfollowup',
            name='contact_resolution',
            field=models.ForeignKey(to='pttrack.ContactResult'),
        ),
        migrations.AddField(
            model_name='generalfollowup',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
        migrations.AddField(
            model_name='document',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='document',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='document',
            name='document_type',
            field=models.ForeignKey(to='pttrack.DocumentType'),
        ),
        migrations.AddField(
            model_name='document',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
        migrations.AddField(
            model_name='clinicdate',
            name='clinic_type',
            field=models.ForeignKey(to='pttrack.ClinicType'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='completion_author',
            field=models.ForeignKey(related_name='action_items_completed', blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='instruction',
            field=models.ForeignKey(to='pttrack.ActionInstruction'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
    ]
