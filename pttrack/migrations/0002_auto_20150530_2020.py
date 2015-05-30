# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicdate',
            name='clinic_type',
            field=models.CharField(default=b'BASIC', max_length=5, choices=[(b'BASIC', b'(Saturday) Basic Care Clinic'), (b'PSYCH', b'Depression & Anxiety Specialty'), (b'ORTHO', b'Muscle and Joint Pain Specialty'), (b'DERMA', b'Dermatology Specialty')]),
        ),
    ]
