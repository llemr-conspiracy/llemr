import csv
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import django.utils.timezone
from django.utils.timezone import now
from pttrack.models import Patient
from demographics.models import Demographics
from workup.models import DiagnosisType

#numpy.warnings.filterwarnings('ignore')

class Command(BaseCommand):
    help = '''Generates CSV statistics for current patient database.'''

    def handle(self, *args, **options):
        #Dictionary of the fields we want to pull for each patient:
        meta = {'filename': 'ptstats.csv','classname': Patient,'fields': ['id','first_name','last_name', 'date_of_birth', 'gender', 'address', 'city', 'state', 'zip_code', 'country']}
        self._write_csv(**meta)
#        self.genmap(meta['filename'])

    def _write_csv(self, filename, classname, fields):
        with open(filename, 'w+') as f:
            writer = csv.writer(f)

            #Patient.latest_workup.clinic_day() is split into the type of clinic and the actual date:
            workupdatefields = ['clinic_type','clinic_date']
            
            #All other fields we want to pull for each note:
            workupfields = ['attending', 'chief_complaint', 'diagnosis']

            #Demographic fields we want to pull:
            demographicfields = ['transportation']

            dx_cats = list(DiagnosisType.objects.all())
            
            #Writes the header (basically just a list of the different Patient & Workup fields we looked up)
            writer.writerow(
                fields +
                workupdatefields +
                workupfields + 
                ['dx_%s' % unicode(dx).lower() for dx in dx_cats] +
                demographicfields)

            #Writes the rows of data
            for obj in classname.objects.all():
                row = [unicode(getattr(obj, field)) for field in fields]
                lastworkup = obj.latest_workup()
                if lastworkup != None:
                    for wudf in workupdatefields:
                        row.append(unicode(getattr(lastworkup.clinic_day, wudf)))
                    for wuf in workupfields:
                        row.append(unicode(getattr(lastworkup, wuf)))

                    dx_v = [0]*len(dx_cats)
                    for dx in lastworkup.diagnosis_categories.all():
                        dx_v[dx_cats.index(dx)] = 1
                    row.extend(dx_v)
                
                try:
                    dem = obj.demographics
                    if dem != None:
                        for demprop in demographicfields:
                            row.append(unicode(getattr(dem, demprop)))
                except Demographics.DoesNotExist:
                    row.append(None)
                writer.writerow([s.encode('utf-8') if hasattr(s, 'encode') else s for s in row])

        print 'Data written to %s' % filename