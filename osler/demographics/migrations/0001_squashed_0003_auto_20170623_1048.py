# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('demographics', '0001_initial'),
                ('demographics', '0002_auto_20160328_1425'),
                ('demographics', '0003_auto_20170623_1048')]

    dependencies = [
        ('pttrack', '0001_squashed_0010_auto_20170623_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChronicCondition',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Demographics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateField(null=True, blank=True)),
                ('has_insurance', models.BooleanField(default=False)),
                ('ER_visit_last_year', models.BooleanField(default=False, verbose_name=b'Visited ER in the past year')),
                ('last_date_physician_visit', models.DateField(null=True, verbose_name=b'Date Last Visited Patient', blank=True)),
                ('lives_alone', models.BooleanField(default=False)),
                ('dependents', models.PositiveSmallIntegerField(null=True, verbose_name=b'Number of Dependents', blank=True)),
                ('currently_employed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='EducationLevel',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncomeRange',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceAccess',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransportationOption',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkStatus',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='demographics',
            name='annual_income',
            field=models.ForeignKey(blank=True, to='demographics.IncomeRange', null=True),
        ),
        migrations.AddField(
            model_name='demographics',
            name='chronic_condition',
            field=models.ManyToManyField(to='demographics.ChronicCondition', blank=True),
        ),
        migrations.AddField(
            model_name='demographics',
            name='education_level',
            field=models.ForeignKey(blank=True, to='demographics.EducationLevel', null=True),
        ),
        migrations.AddField(
            model_name='demographics',
            name='patient',
            field=models.OneToOneField(null=True, to='pttrack.Patient'),
        ),
        migrations.AddField(
            model_name='demographics',
            name='resource_access',
            field=models.ManyToManyField(to='demographics.ResourceAccess', verbose_name=b'Access to Resources', blank=True),
        ),
        migrations.AddField(
            model_name='demographics',
            name='transportation',
            field=models.ForeignKey(blank=True, to='demographics.TransportationOption', null=True),
        ),
        migrations.AddField(
            model_name='demographics',
            name='work_status',
            field=models.ForeignKey(blank=True, to='demographics.WorkStatus', null=True),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='ER_visit_last_year',
            field=models.NullBooleanField(verbose_name=b'Visited ER in the past year'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='currently_employed',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='has_insurance',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='lives_alone',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='ER_visit_last_year',
            field=models.NullBooleanField(verbose_name=b'Visited ER in the Past Year'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='last_date_physician_visit',
            field=models.DateField(null=True, verbose_name=b"Date of Patient's Last Visit to Physician or ER", blank=True),
        ),
    ]
