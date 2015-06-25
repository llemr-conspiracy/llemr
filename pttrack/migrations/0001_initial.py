# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import pttrack.models


class Migration(migrations.Migration):

    dependencies = [
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
                ('written_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('due_date', models.DateField()),
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
            ],
        ),
        migrations.CreateModel(
            name='DiagnosisType',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('long_name', models.CharField(max_length=30)),
                ('short_name', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='GeneralFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LabFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(default=django.utils.timezone.now)),
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
                ('phone', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(default=b'St. Louis', max_length=50)),
                ('state', models.CharField(default=b'MO', max_length=2)),
                ('zip_code', models.CharField(max_length=5, validators=[pttrack.models.validate_zip])),
                ('date_of_birth', models.DateField()),
                ('ethnicity', models.ForeignKey(to='pttrack.Ethnicity')),
                ('gender', models.ForeignKey(to='pttrack.Gender')),
                ('language', models.ForeignKey(to='pttrack.Language')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PCPLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('address', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('gender', models.ForeignKey(to='pttrack.Gender')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProviderType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('long_name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='ReferralFollowup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('comments', models.TextField(null=True, blank=True)),
                ('has_appointment', models.BooleanField(help_text=b'Does the patient have an appointment?')),
                ('pt_showed', models.CharField(blank=True, max_length=7, null=True, help_text=b'Did the patient show up to the appointment?', choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Not yet', b'Not yet')])),
                ('apt_location', models.ForeignKey(blank=True, to='pttrack.PCPLocation', help_text=b'Where is the appointment?', null=True)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('contact_method', models.ForeignKey(to='pttrack.ContactMethod')),
                ('contact_resolution', models.ForeignKey(to='pttrack.ContactResult')),
                ('noapt_reason', models.ForeignKey(blank=True, to='pttrack.NoAptReason', help_text=b"If the patient didn't make an appointment, why not?", null=True)),
                ('noshow_reason', models.ForeignKey(blank=True, to='pttrack.NoShowReason', help_text=b"If the patient didn't go to appointment, why not?", null=True)),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
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
                ('written_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('comments', models.TextField(null=True, blank=True)),
                ('subsq_dose', models.BooleanField(help_text=b'Are they coming back for another dose?')),
                ('dose_date', models.DateField(help_text=b'When is the next dose?', null=True, blank=True)),
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
                ('chief_complaint', models.CharField(max_length=1000, verbose_name=b'CC')),
                ('diagnosis', models.CharField(max_length=1000, verbose_name=b'Dx')),
                ('HPI', models.TextField(verbose_name=b'HPI')),
                ('PMH_PSH', models.TextField(verbose_name=b'PMH/PSH')),
                ('meds', models.TextField()),
                ('allergies', models.TextField()),
                ('fam_hx', models.TextField()),
                ('soc_hx', models.TextField()),
                ('ros', models.TextField()),
                ('hr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('bp', models.CharField(blank=True, max_length=7, null=True, validators=[pttrack.models.validate_bp])),
                ('rr', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('t', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
                ('pe', models.TextField()),
                ('labs_ordered_quest', models.TextField(null=True, blank=True)),
                ('labs_ordered_internal', models.TextField(null=True, blank=True)),
                ('rx', models.TextField(null=True, blank=True)),
                ('got_voucher', models.BooleanField(default=False)),
                ('voucher_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('patient_pays', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('will_return', models.BooleanField(default=False)),
                ('A_and_P', models.TextField()),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('clinic_day', models.ForeignKey(to='pttrack.ClinicDate')),
                ('diagnosis_category', models.ForeignKey(to='pttrack.DiagnosisType')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
                ('referral_location', models.ForeignKey(blank=True, to='pttrack.PCPLocation', null=True)),
                ('referral_type', models.ForeignKey(blank=True, to='pttrack.ReferralType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='referralfollowup',
            name='referral_type',
            field=models.ForeignKey(help_text=b'What kind of provider was the patient referred to?', to='pttrack.ReferralType'),
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
