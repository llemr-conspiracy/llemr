# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0003_auto_20160119_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChronicConditions',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='EducationLevel',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncomeRanges',
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
            name='TransportationOptions',
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
            model_name='historicalpatient',
            name='ER_visit_last_year',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='currently_employed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='dependents',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='has_insurance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='last_date_physician_visit',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='lives_alone',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='patient',
            name='ER_visit_last_year',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='patient',
            name='currently_employed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='patient',
            name='dependents',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='has_insurance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='patient',
            name='last_date_physician_visit',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='lives_alone',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='annual_income',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.IncomeRanges', null=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='chronic_condition',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ChronicConditions', null=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='education_level',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.EducationLevel', null=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='resource_access',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ResourceAccess', null=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='transportation',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.TransportationOptions', null=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='work_status',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.WorkStatus', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='annual_income',
            field=models.ForeignKey(blank=True, to='pttrack.IncomeRanges', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='chronic_condition',
            field=models.ForeignKey(blank=True, to='pttrack.ChronicConditions', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='education_level',
            field=models.ForeignKey(blank=True, to='pttrack.EducationLevel', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='resource_access',
            field=models.ForeignKey(blank=True, to='pttrack.ResourceAccess', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='transportation',
            field=models.ForeignKey(blank=True, to='pttrack.TransportationOptions', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='work_status',
            field=models.ForeignKey(blank=True, to='pttrack.WorkStatus', null=True),
        ),
    ]
