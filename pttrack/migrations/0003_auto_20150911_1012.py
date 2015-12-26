# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0002_added_documents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vaccinefollowup',
            name='dose_date',
            field=models.DateField(help_text=b'When does the patient want to get their next dose (if applicable)?', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='vaccinefollowup',
            name='subsq_dose',
            field=models.BooleanField(verbose_name=b'Has the patient committed to coming back for another dose?'),
        ),
    ]
