# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pttrack.models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0005_auto_20150915_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='image',
            field=models.FileField(help_text=b'Please deidentify all file names before upload! Delete all files after upload!', upload_to=pttrack.models.make_filepath, verbose_name=b'PDF File or Image Upload'),
        ),
        migrations.AlterField(
            model_name='historicaldocument',
            name='image',
            field=models.TextField(help_text=b'Please deidentify all file names before upload! Delete all files after upload!', max_length=100, verbose_name=b'PDF File or Image Upload'),
        ),
    ]
