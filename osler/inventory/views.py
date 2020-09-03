# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
import urllib

from . import models
from . import forms
from . import utils

from tempfile import NamedTemporaryFile
import csv
from datetime import date

# Create your views here.
class DrugListView(ListView):
    template_name = 'inventory/inventory-main.html'
    def get_queryset(self):
        druglist = models.Drug.objects.\
                    select_related('unit').\
                    select_related('category').\
                    select_related('manufacturer').\
                    order_by('category', 'name').\
                    exclude(stock=0).all()
        return druglist


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
        # Call the base implementation first to get a context
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
    drug = get_object_or_404(models.Drug, id=pk)
    can_dispense = drug.can_dispense(int(num))
    if can_dispense:
        drug.dispense(int(num))
    else:
        return HttpResponseNotFound('<h1>Cannot dispense more drugs than in stock!</h1>')
    return redirect('inventory:drug-list')

def export_csv(request):
    '''Writes drug models to a new .csv file saved the project root-level folder'''
    drugs = models.Drug.objects.\
        select_related('unit').\
        select_related('category').\
        select_related('manufacturer').\
        order_by('category', 'name')

    
    # csv_file = open(csv_filename, 'w')
    with NamedTemporaryFile(mode='a+') as file:
        writer = csv.writer(file)
        header = ['Drug Name', 'Dose', 'Unit', 'Stock', 'Expiration Date',
                  'Lot Number', 'Category', 'Manufacturer']
        writer.writerow(header)
        for drug in drugs:
            writer.writerow(
                [drug.name,
                 drug.dose,
                 drug.unit,
                 drug.stock,
                 drug.expiration_date,
                 drug.lot_number,
                 drug.category,
                 drug.manufacturer])
        file.seek(0)
        csvfileread = file.read()

    csv_filename = ''.join(['drug-inventory-',str(date.today()),'.csv'])

    response = HttpResponse(csvfileread, 'application/csv')
    response["Content-Disposition"] = (
        "attachment; filename=%s" % (csv_filename,))

    return response
