# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0002_providertype_is_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionitem',
            name='comments',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='historicalactionitem',
            name='comments',
            field=models.TextField(),
        ),
    ]
