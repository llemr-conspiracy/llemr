# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0002_auto_20150531_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='email',
            field=models.EmailField(default='justinrporter@wustl.edu', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='provider_type',
            field=models.CharField(default='PRECLIN', max_length=6, choices=[(b'ATTEND', b'Attending Physician'), (b'CLIN', b'Clinical Medical Student'), (b'PRECLIN', b'Preclinical Medical Student')]),
            preserve_default=False,
        ),
    ]
