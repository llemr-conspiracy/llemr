# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0008_auto_20151027_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactresult',
            name='patient_reached',
            field=models.BooleanField(default=True, help_text=b'True if the outcome means they did not reach the patient'),
        ),
        migrations.AlterField(
            model_name='referralfollowup',
            name='referral_type',
            field=models.ForeignKey(blank=True, to='pttrack.ReferralType', help_text=b'What kind of provider was the patient referred to?', null=True),
        ),
    ]
