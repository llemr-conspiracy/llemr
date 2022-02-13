# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pdb

from django.shortcuts import redirect
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
import urllib
from osler.users.decorators import active_permission_required
from osler.users.utils import get_active_role, group_has_perm

from osler.core.views import NoteFormView
from osler.core.models import Patient
from osler.users.utils import get_active_role

from . import models
from . import forms
from . import utils

from tempfile import NamedTemporaryFile
import csv
import datetime
from django.utils import timezone

order_list = ['name', 'dose', 'expiration_date']
class DrugListView(ListView):
    template_name = 'inventory/inventory-main.html'
    def get_queryset(self):
        druglist = models.Drug.objects.\
                    select_related('unit').\
                    select_related('category').\
                    select_related('manufacturer').\
                    order_by(*order_list).\
                    exclude(stock=0).all()
        return druglist

    def get_context_data(self, **kwargs):
        context = super(DrugListView, self).get_context_data(**kwargs)
        context['patients'] = Patient.objects.filter(encounter__status__is_active=True)\
            .order_by('last_name').select_related('gender')

        active_role = get_active_role(self.request)
        context['can_export_csv'] = group_has_perm(active_role, 'inventory.export_csv')
        return context

class PreDrugAddNew(FormView):
    template_name = 'inventory/pre_add_new_drug.html'
    form_class = forms.DuplicateDrugForm

    def form_valid(self, form):
        name_str = form.cleaned_data['name'].capitalize()
        lot_number_str = form.cleaned_data['lot_number'].upper()
        manufacturer_str = form.cleaned_data['manufacturer']

        q = {
            "name": name_str,
            "lot_number": lot_number_str,
            "manufacturer": manufacturer_str
        }

        querystr = urllib.parse.urlencode(q)

        add_new_drug_url = "%s?%s" % (reverse("inventory:drug-add-new"), querystr)

        matching_drugs = models.Drug.objects.filter(name=name_str, lot_number=lot_number_str, manufacturer=manufacturer_str)

        if len(matching_drugs) > 0:
            predrug_select_url = "%s?%s" % (reverse("inventory:predrug-select"), querystr)
            return HttpResponseRedirect(predrug_select_url)

        return HttpResponseRedirect(add_new_drug_url)

class PreDrugSelect(ListView):
    template_name = 'inventory/predrug-select.html'
    new_drug_url = ""

    def parse_url_querystring(self):

        return utils.get_name_and_lot_from_url_query_dict(self.request)

    def get_queryset(self):
        initial = self.parse_url_querystring()
        possible_duplicates = models.Drug.objects.filter(name=initial.get('name', None),\
                                                        lot_number=initial.get('lot_number', None),\
                                                        manufacturer=initial.get('manufacturer', None))
        return possible_duplicates

    def get_context_data(self, **kwargs):
        context = super(PreDrugSelect, self).get_context_data(**kwargs)
        initial = self.parse_url_querystring()
        context['name'] = initial.get('name', None)
        context['lot_number'] = initial.get('lot_number', None)
        context['manufacturer'] = initial.get('manufacturer', None)
        u = {
            "name": initial.get('name', None),
            "lot_number": initial.get('lot_number', None),
            "manufacturer": initial.get('manufacturer', None)
        }
        url = urllib.parse.urlencode(u)
        context['new_drug_url'] = "%s?%s" % (reverse("inventory:drug-add-new"), url)
        context['home'] = reverse("inventory:drug-list")
        return context

class DrugAddNew(FormView):
    template_name = 'inventory/add_new_drug.html'
    form_class = forms.DrugForm

    def form_valid(self, form):
        df = form.save()
        df.save()
        return redirect('inventory:drug-list')

    def get_initial(self):
        initial = super(DrugAddNew, self).get_initial()

        initial.update(utils.get_name_and_lot_from_url_query_dict(self.request))
        return initial


class DrugUpdate(UpdateView):
    template_name = 'inventory/update_drug.html'
    model = models.Drug
    form_class = forms.DrugForm

    def form_valid(self, form):
        df = form.save()
        df.save()
        return redirect('inventory:drug-list')


def drug_dispense(request):
    pk = request.POST['pk']
    num = request.POST['num']

    patient_pk = request.POST['patient_pk']
    drug = models.Drug.objects.get(pk=pk)
    patient = Patient.objects.get(pk=patient_pk)
    can_dispense = drug.can_dispense(int(num))    

    if can_dispense:
        models.DispenseHistory.objects.create(drug=drug,
                                              dispense=num,
                                              author=request.user,
                                              author_type=get_active_role(request),
                                              patient=patient,
                                              encounter=patient.last_encounter())
        drug.dispense(int(num))
    else:
        return HttpResponseNotFound('<h1>Cannot dispense more drugs than in stock!</h1>')
    return redirect('inventory:drug-list')


@active_permission_required('inventory.export_csv', raise_exception=True)
def export_csv(request):
    '''Writes drug models to a new .csv file saved the project root-level folder'''
    drugs = models.Drug.objects.\
        select_related('unit').\
        select_related('category').\
        select_related('manufacturer').\
        order_by(*order_list)

    day_interval = timezone.make_aware(timezone.datetime.today() - datetime.timedelta(days=6))
    recently_dispensed = models.DispenseHistory.objects.filter(written_datetime__gte=day_interval)

    with NamedTemporaryFile(mode='a+') as file:
        writer = csv.writer(file)
        header = ['Drug Name', 'Dosage', 'Unit', 'Category', 'Stock Remaining', 'Lot Number',
        'Expiration Date', 'Manufacturer', f"Doses Dispensed Since {format_date(str(day_interval.date()))}"]
        writer.writerow(header)
        for drug in drugs:
            dispensed_list = list(recently_dispensed.filter(drug=drug.id).values_list('dispense', flat=True))
            dispensed_sum = sum(dispensed_list)
            if dispensed_sum == 0:
                dispensed_sum = ""
            writer.writerow(
                [drug.name,
                 drug.dose,
                 drug.unit,
                 drug.category,
                 drug.stock,
                 drug.lot_number,
                 drug.expiration_date,
                 drug.manufacturer,
                 dispensed_sum
                 ])
        file.seek(0)
        csvfileread = file.read()

    csv_filename = f"drug-inventory-{format_date(str(timezone.now().date()))}.csv"

    response = HttpResponse(csvfileread, 'application/csv')
    response["Content-Disposition"] = (
        "attachment; filename=%s" % (csv_filename,))

    return response

@active_permission_required('inventory.export_csv', raise_exception=True)
def export_dispensing_history(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    tz_aware_start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
    tz_aware_end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
    tz_aware_end_date_plus_one = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1))

    recent_dispense_histories = models.DispenseHistory.objects.exclude(
        written_datetime__gt=tz_aware_end_date_plus_one).filter(written_datetime__gte=tz_aware_start_date)

    recently_dispensed_drugs = models.Drug.objects.filter(pk__in=list(recent_dispense_histories.values_list('drug', flat=True)))
    recently_dispensed_drugs.select_related('unit').\
        select_related('category').\
        select_related('manufacturer').\
        order_by(*order_list)

    with NamedTemporaryFile(mode='a+') as file:
        writer = csv.writer(file)
        header = ['Drug Name', f"Doses Dispensed From: {format_date(str(tz_aware_start_date.date()))} - {format_date(str(tz_aware_end_date.date()))}",
                  'Stock Remaining ', 'Dosage', 'Unit', 'Category', 'Lot Number', 'Expiration Date', 'Manufacturer']
        writer.writerow(header)
        for drug in recently_dispensed_drugs:
            dispensed_list = list(recent_dispense_histories.filter(drug=drug.id).values_list('dispense', flat=True))
            dispensed_sum = sum(dispensed_list)
            writer.writerow(
                [drug.name,
                dispensed_sum,
                drug.stock,
                drug.dose,
                drug.unit,
                drug.category,
                drug.lot_number,
                drug.expiration_date,
                drug.manufacturer
                ])
        file.seek(0)
        csvfileread = file.read()

    csv_filename = f"drug-dispensing-history-through-{format_date(str(tz_aware_end_date.date()))}.csv"
    response = HttpResponse(csvfileread, 'application/csv')
    response["Content-Disposition"] = (
        "attachment; filename=%s" % (csv_filename,))
    redirect('inventory:drug-list')
    return response

def format_date(date):
    date_list = date.split("-")
    formatted_date = f"{date_list[1]}/{date_list[2]}/{date_list[0][:2]}"
    return formatted_date
