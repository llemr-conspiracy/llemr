# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


def update_hisorical_ssn(apps, schema_editor):
    Patient = apps.get_model("pttrack", "Patient")

    for pt in Patient.objects.all():

        if pt.ssn == '--' or pt.ssn == '':
            pt.ssn = None
        elif r'[0-9]{3}-[0-9]{2}-[0-9]{2}'.match(pt.ssn):
            # PANIC!
            assert False


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0005_auto_20160628_1852'),
    ]

    operations = [
        migrations.RunPython(update_hisorical_ssn),
        migrations.AlterField(
            model_name='historicalpatient',
            name='ssn',
            field=models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator(regex=b'[0-9]{3}-[0-9]{2}-[0-9]{4}')]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='ssn',
            field=models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator(regex=b'[0-9]{3}-[0-9]{2}-[0-9]{4}')]),
        ),
    ]
