# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pttrack.validators


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0004_auto_20160328_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprovider',
            name='needs_updating',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='needs_updating',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='first_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='last_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='historicalprovider',
            name='first_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='historicalprovider',
            name='last_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='historicalprovider',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='first_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='last_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='provider',
            name='first_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='provider',
            name='last_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='provider',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name]),
        ),
    ]
