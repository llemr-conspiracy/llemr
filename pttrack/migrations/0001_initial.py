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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instruction', models.CharField(max_length=50)),
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
            name='Ethnicity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Followup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField()),
                ('written_datetime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
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
            name='Language',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
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
            name='Workup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chief_complaint', models.CharField(max_length=300)),
                ('HandP', models.TextField()),
                ('AandP', models.TextField()),
                ('diagnosis', models.CharField(max_length=100)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('clinic_day', models.ForeignKey(to='pttrack.ClinicDate')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='followup',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='followup',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='followup',
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
