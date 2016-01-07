# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalworkup',
            name='fam_hx',
            field=models.TextField(verbose_name=b'Family History'),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='labs_ordered_internal',
            field=models.TextField(null=True, verbose_name=b'Labs Ordered Internally', blank=True),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='labs_ordered_quest',
            field=models.TextField(null=True, verbose_name=b'Labs Ordered from Quest', blank=True),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='ros',
            field=models.TextField(verbose_name=b'ROS'),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='rx',
            field=models.TextField(null=True, verbose_name=b'Prescription Orders', blank=True),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='soc_hx',
            field=models.TextField(verbose_name=b'Social History'),
        ),
        migrations.AlterField(
            model_name='workup',
            name='fam_hx',
            field=models.TextField(verbose_name=b'Family History'),
        ),
        migrations.AlterField(
            model_name='workup',
            name='labs_ordered_internal',
            field=models.TextField(null=True, verbose_name=b'Labs Ordered Internally', blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='labs_ordered_quest',
            field=models.TextField(null=True, verbose_name=b'Labs Ordered from Quest', blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='ros',
            field=models.TextField(verbose_name=b'ROS'),
        ),
        migrations.AlterField(
            model_name='workup',
            name='rx',
            field=models.TextField(null=True, verbose_name=b'Prescription Orders', blank=True),
        ),
        migrations.AlterField(
            model_name='workup',
            name='soc_hx',
            field=models.TextField(verbose_name=b'Social History'),
        ),
    ]
