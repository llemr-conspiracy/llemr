# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pttrack.validators


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0008_add_case_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpatient',
            name='date_of_birth',
            field=models.DateField(help_text=b'MM/DD/YYYY', validators=[pttrack.validators.validate_birth_date]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='date_of_birth',
            field=models.DateField(help_text=b'MM/DD/YYYY', validators=[pttrack.validators.validate_birth_date]),
        ),
    ]
