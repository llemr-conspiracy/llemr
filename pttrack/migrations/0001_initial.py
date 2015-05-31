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
            name='ClinicDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('clinic_type', models.CharField(default=b'BASIC', max_length=5, choices=[(b'BASIC', b'(Saturday) Basic Care Clinic'), (b'PSYCH', b'Depression & Anxiety Specialty'), (b'ORTHO', b'Muscle and Joint Pain Specialty'), (b'DERMA', b'Dermatology Specialty')])),
                ('date', models.DateField()),
                ('gcal_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('language_name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')])),
            ],
        ),
        migrations.CreateModel(
            name='Followup',
            fields=[
                ('note_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pttrack.Note')),
                ('note', models.TextField()),
                ('written_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('next_action', models.DateField(blank=True)),
            ],
            bases=('pttrack.note',),
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('person_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pttrack.Person')),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(default=b'St. Louis', max_length=50)),
                ('state', models.CharField(default=b'MO', max_length=2)),
                ('zip_code', models.CharField(max_length=5, validators=[pttrack.models.validate_zip])),
                ('date_of_birth', models.DateField()),
                ('ethnicity', models.CharField(max_length=50)),
                ('comp_status', models.CharField(max_length=4, choices=[(b'LTFO', b'Filed - Lost to follow up'), (b'COMP', b'Filed - encounter completed'), (b'BIN', b'In WashU Bin'), (b'PCP', b'PCP Referral Follow-up')])),
                ('language', models.ForeignKey(to='pttrack.Language')),
            ],
            bases=('pttrack.person',),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('person_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pttrack.Person')),
            ],
            bases=('pttrack.person',),
        ),
        migrations.CreateModel(
            name='Workup',
            fields=[
                ('note_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pttrack.Note')),
                ('CC', models.CharField(max_length=300)),
                ('HPI', models.TextField()),
                ('PMH', models.TextField()),
                ('PSH', models.TextField()),
                ('SocHx', models.TextField()),
                ('FamHx', models.TextField()),
                ('allergies', models.TextField()),
                ('meds', models.TextField()),
                ('diagnosis', models.CharField(max_length=100)),
                ('labs', models.TextField()),
                ('plan', models.TextField()),
                ('clinic_day', models.ForeignKey(to='pttrack.ClinicDate')),
            ],
            bases=('pttrack.note',),
        ),
        migrations.AddField(
            model_name='note',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider', blank=True),
        ),
        migrations.AddField(
            model_name='note',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
    ]
