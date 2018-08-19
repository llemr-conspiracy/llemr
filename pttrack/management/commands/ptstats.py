import csv
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import django.utils.timezone
from django.utils.timezone import now
from pttrack.models import Patient
from workup.models import DiagnosisType
import geopy
import gmplot
import numpy
import pandas

numpy.warnings.filterwarnings('ignore')

class Command(BaseCommand):
    help = '''Generates CSV statistics for current patient database.'''

    def handle(self, *args, **options):
        #Dictionary of the fields we want to pull for each patient:
        meta = {'filename': 'ptstats.csv','classname': Patient,'fields': ['id', 'address', 'city', 'state', 'zip_code', 'country']}
        self._write_csv(**meta)
        self.genmap(meta['filename'])

    def _write_csv(self, filename, classname, fields):
        with open(filename, 'w+') as f:
            writer = csv.writer(f)

            #Patient.latest_workup.clinic_day() is split into the type of clinic and the actual date:
            workupdatefields = ['clinic_type','clinic_date']
            
            #All other fields we want to pull for each note:
            workupfields = ['attending', 'chief_complaint', 'diagnosis']


            dx_cats = list(DiagnosisType.objects.all())
            
            #Writes the header (basically just a list of the different Patient & Workup fields we looked up)
            writer.writerow(
                fields +
                workupdatefields +
                workupfields + 
                ['dx_%s' % unicode(dx).lower() for dx in dx_cats])

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
                writer.writerow(row)

        print 'Data written to %s' % filename

    def genmap(self, filename):
        geolocator = geopy.geocoders.Nominatim(user_agent="osler")
        gmap = gmplot.gmplot.GoogleMapPlotter.from_geocode("St. Louis MO")
        heatmap = gmplot.gmplot.GoogleMapPlotter.from_geocode("St. Louis MO")
        df = pandas.read_csv(filename)
        addresslst = df.address
        citylst = df.city
        statelst = df.state
        geodata = []
        for i in xrange(0,len(addresslst)):
            newadd = addresslst[i] + ', ' + citylst[i] + ', ' + statelst[i]
            geodata.append(newadd)
        coordslst = []
        for geodatum in geodata:
            location = geolocator.geocode(geodatum)
            if location != None:
                coords = ((location.latitude, location.longitude))
                coordslst.append(coords)
        latslst,longslst = zip(*coordslst)
        for z in xrange(0,len(latslst)):
            gmap.marker(latslst[z],longslst[z],'cornflowerblue')
        gmap.draw("map.html")
        heatmap.heatmap(latslst,longslst)
        heatmap.draw("heatmap.html")
        print "Maps of patient address data generated as 'map.html' and 'heatmap.html'"
