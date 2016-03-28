# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demographics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demographics',
            name='ER_visit_last_year',
            field=models.NullBooleanField(verbose_name=b'Visited ER in the past year'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='chronic_condition',
            field=models.ManyToManyField(to='demographics.ChronicCondition', blank=True),
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
            name='resource_access',
            field=models.ManyToManyField(to='demographics.ResourceAccess', verbose_name=b'Access to Resources', blank=True),
        ),
    ]
