# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pttrack', '0003_auto_20171014_1843'),
        ('demographics', '0001_squashed_0003_auto_20170623_1048'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalDemographics',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('creation_date', models.DateField(null=True, blank=True)),
                ('has_insurance', models.NullBooleanField(choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')])),
                ('ER_visit_last_year', models.NullBooleanField(verbose_name=b'Visited ER in the Past Year', choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')])),
                ('last_date_physician_visit', models.DateField(null=True, verbose_name=b"Date of Patient's Last Visit to Physician or ER", blank=True)),
                ('lives_alone', models.NullBooleanField(choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')])),
                ('dependents', models.PositiveSmallIntegerField(null=True, verbose_name=b'Number of Dependents', blank=True)),
                ('currently_employed', models.NullBooleanField(choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('annual_income', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='demographics.IncomeRange', null=True)),
                ('education_level', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='demographics.EducationLevel', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True)),
                ('transportation', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='demographics.TransportationOption', null=True)),
                ('work_status', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='demographics.WorkStatus', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical demographics',
            },
        ),
        migrations.AlterField(
            model_name='demographics',
            name='ER_visit_last_year',
            field=models.NullBooleanField(verbose_name=b'Visited ER in the Past Year', choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')]),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='currently_employed',
            field=models.NullBooleanField(choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')]),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='has_insurance',
            field=models.NullBooleanField(choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')]),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='lives_alone',
            field=models.NullBooleanField(choices=[(None, b'Not Answered'), (True, b'Yes'), (False, b'No')]),
        ),
    ]
