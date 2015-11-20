# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pttrack.models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0007_auto_20151004_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpatient',
            name='ssn',
            field=models.CharField(blank=True, max_length=9, null=True, validators=[pttrack.models.validate_ssn]),
        ),
        migrations.AddField(
            model_name='patient',
            name='ssn',
            field=models.CharField(blank=True, max_length=9, null=True, validators=[pttrack.models.validate_ssn]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='languages',
            field=models.ManyToManyField(help_text=b'Specify here languages that are spoken at a level sufficient to be used for medical communication.', to='pttrack.Language'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='languages',
            field=models.ManyToManyField(help_text=b'Specify here languages that are spoken at a level sufficient to be used for medical communication.', to='pttrack.Language'),
        ),
    ]
