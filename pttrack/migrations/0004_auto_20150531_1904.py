# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0003_auto_20150531_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='person_ptr',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='person_ptr',
        ),
        migrations.AddField(
            model_name='patient',
            name='first_name',
            field=models.CharField(default='John', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='gender',
            field=models.CharField(default='M', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, default=1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='last_name',
            field=models.CharField(default='Doe', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='middle_name',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='phone',
            field=models.CharField(default='4252439115', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='first_name',
            field=models.CharField(default='Joe', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='gender',
            field=models.CharField(default='F', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, default=2, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='last_name',
            field=models.CharField(default='doe', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='middle_name',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='phone',
            field=models.CharField(default=123123, max_length=50),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]
