# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0003_auto_20160119_1459'),
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
            field=models.ManyToManyField(to='demographics.ChronicCondition', null=True, blank=True),
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
            field=models.ManyToManyField(to='demographics.ResourceAccess', null=True, verbose_name=b'Access to Resources', blank=True),
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
    ]
