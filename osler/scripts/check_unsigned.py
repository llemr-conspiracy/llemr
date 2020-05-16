from __future__ import print_function
from __future__ import unicode_literals
from datetime import date
from osler.core.models import Provider
from osler.workup.models import Workup

unsigned_workups = Workup.objects.filter(signer=None)

print(unsigned_workups)

for wu in unsigned_workups:
    d = wu.clinic_day.clinic_date
    providers = Provider.objects.filter(
        signed_workups__in=Workup.objects.filter(
            clinic_day__clinic_date=d)).distinct()
    print(wu.patient, providers, d)
