# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from django.http import HttpResponseRedirect

from . import models
from . import forms
from . import utils

# Create your views here.


def drug_list(request):
    drugs = models.Drug.objects.all().order_by('name')
    drug_types = {
        'drugs': drugs,
    }

    return render(request, 'inventory/inventory-main.html', drug_types)

class PreDrugAddNew(FormView):
    template_name = 'inventory/pre_add_new_drug.html'
    form_class = forms.DuplicateDrugForm

    def form_valid(self, form):
        name_str = form.cleaned_data['name'].capitalize()
        lot_number_str = form.cleaned_data['lot_number']

        querystr = '%s=%s&%s=%s' % ("name", name_str,
                                    "lot_number", lot_number_str)

        add_new_drug_url = "%s?%s" % (reverse("drug-add-new"), querystr)

        if lot_number_str.strip() == '':
            return HttpResponseRedirect(add_new_drug_url)

        matching_drugs = models.Drug.objects.filter(lot_number=lot_number_str)

        if len(matching_drugs) > 0:
            predrug_select_url = "%s?%s" % (reverse("predrug-select"), querystr)
            return HttpResponseRedirect(predrug_select_url)

        return HttpResponseRedirect(add_new_drug_url)

class PreDrugSelect(ListView):
    template_name = 'inventory/predrug-select.html'
    new_drug_url = ""

    def parse_url_querystring(self):

        return utils.get_name_and_lot_from_url_query_dict(self.request)

    def get_queryset(self):
        initial = self.parse_url_querystring()
        if (initial.get('name', None) is None):
            return []
        possible_duplicates = models.Drug.objects.filter(lot_number=initial.get('lot_number', None))
        return possible_duplicates

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PreDrugSelect, self).get_context_data(**kwargs)
        initial = self.parse_url_querystring()
        context['name'] = initial.get('name', None)
        context['lot_number'] = initial.get('lot_number', None)
        context['new_drug_url'] = "%s?%s=%s&%s=%s" % (
            reverse("drug-add-new"),
            "name", initial.get('name', None),
            "lot_number", initial.get('lot_number', None))
        context['home'] = reverse("drug-list")
        return context

class DrugAddNew(FormView):
    template_name = 'inventory/add_new_drug.html'
    form_class = forms.DrugForm

    def form_valid(self, form):
        df = form.save()
        df.save()
        return redirect('drug-list')

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
        return redirect('drug-list')

def drug_delete(request, pk):
    drug = get_object_or_404(models.Drug, id=pk)
    drug.delete()
    return redirect('drug-list')

def drug_add(request):
    pk = request.POST['pk']
    num = request.POST['num']
    drug = get_object_or_404(models.Drug, id=pk)
    drug.stock += int(num)
    drug.save()
    return redirect('drug-list')

def drug_dispense(request):
    pk = request.POST['pk']
    num = request.POST['num']
    drug = get_object_or_404(models.Drug, id=pk)
    drug.stock -= int(num)
    if drug.stock < 0:
        drug.stock = 0
    drug.save()
    return redirect('drug-list')
