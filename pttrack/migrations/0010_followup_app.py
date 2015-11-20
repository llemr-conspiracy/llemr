# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0009_auto'),
    ]

    database_operations = [
        migrations.AlterModelTable('GeneralFollowup',
                                   'followup_generalfollowup'),
        migrations.AlterModelTable('HistoricalGeneralFollowup',
                                   'followup_historicalgeneralfollowup'),
        migrations.AlterModelTable('LabFollowup',
                                   'followup_labfollowup'),
        migrations.AlterModelTable('HistoricalLabFollowup',
                                   'followup_historicallabfollowup'),
        migrations.AlterModelTable('ReferralFollowup',
                                   'followup_referralfollowup'),
        migrations.AlterModelTable('HistoricalReferralFollowup',
                                   'followup_historicalreferralfollowup'),
        migrations.AlterModelTable('VaccineFollowup',
                                   'followup_vaccinefollowup'),
        migrations.AlterModelTable('HistoricalVaccineFollowup',
                                   'followup_historicalvaccinefollowup'),
        migrations.AlterModelTable('ContactResult',
                                   'followup_contactresult'),
        migrations.AlterModelTable('NoAptReason',
                                   'followup_noaptreason'),
        migrations.AlterModelTable('NoShowReason',
                                   'followup_noshowreason')
    ]

    state_operations = [
        migrations.DeleteModel('GeneralFollowup'),
        migrations.DeleteModel('HistoricalGeneralFollowup'),
        migrations.DeleteModel('LabFollowup'),
        migrations.DeleteModel('HistoricalLabFollowup'),
        migrations.DeleteModel('ReferralFollowup'),
        migrations.DeleteModel('HistoricalReferralFollowup'),
        migrations.DeleteModel('VaccineFollowup'),
        migrations.DeleteModel('HistoricalVaccineFollowup'),
        migrations.DeleteModel('ContactResult'),
        migrations.DeleteModel('NoAptReason'),
        migrations.DeleteModel('NoShowReason'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
