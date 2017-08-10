# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demographics', '0002_auto_20160328_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demographics',
            name='ER_visit_last_year',
            field=models.NullBooleanField(verbose_name=b'Visited ER in the Past Year'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='last_date_physician_visit',
            field=models.DateField(null=True, verbose_name=b"Date of Patient's Last Visit to Physician or ER", blank=True),
        ),
    ]
