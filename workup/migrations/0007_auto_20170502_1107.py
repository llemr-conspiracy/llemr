# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
#import workup.validators

def split_bp(apps, schema_editor):
	Workup = apps.get_model('workup','Workup')
	for workup_note in Workup.objects.all():
		bp = workup_note.bp
		(workup_note.bp_sys, workup_note.bp_dia) = bp.split('/')
		workup_note.save()

class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0005_auto_20160826_0620'),
    ]

    operations = [
    	migrations.AddField(
            model_name='historicalworkup',
            name='bp_dia',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Diastolic'),
        ),
        migrations.AddField(
            model_name='historicalworkup',
            name='bp_sys',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Systolic'),
        ),
        migrations.AddField(
            model_name='workup',
            name='bp_dia',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Diastolic'),
        ),
        migrations.AddField(
            model_name='workup',
            name='bp_sys',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=b'Systolic'),
        ),
        migrations.RunPython(split_bp),
        migrations.RemoveField(
            model_name='historicalworkup',
            name='bp',
        ),
        migrations.RemoveField(
            model_name='workup',
            name='bp',
        ),
    ]
