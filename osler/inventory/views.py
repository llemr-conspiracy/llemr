# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.shortcuts import render
import urllib

from osler.core.views import NoteFormView
from osler.core.models import Patient
from osler.users.utils import get_active_role


from . import models
from . import forms
from . import utils

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

def select_patient(request, pk):
    if request.method == 'POST':
        form = forms.SelectPatientForm(request.POST)
        if form.is_valid():
            # Get series from form
            patient = form.cleaned_data['patient']

            return HttpResponseRedirect(reverse('inventory:dispense-drug',
                                            kwargs={'pk': pk,'pt_id': patient.id}))
    else:
        form = forms.SelectPatientForm()

        drug = get_object_or_404(models.Drug, id=pk)

        return render(request,'inventory/select-patient.html',{'form': form, 'drug': drug})

class DispenseDrug(NoteFormView):
    # return HttpResponse("Success!")
    template_name = 'inventory/dispense-drug.html'
    note_type = "Dispense Drug"
    form_class = forms.DispenseDrugForm

    def get_context_data(self, **kwargs):
        context = super(DispenseDrug, self).get_context_data(**kwargs)
        context['drug'] = models.Drug.objects.get(pk=self.kwargs['pk'])

        return context

    def get_form_kwargs(self):
        kwargs = super(DispenseDrug, self).get_form_kwargs()
        drug_id = self.kwargs['pk']
        kwargs['pk'] = drug_id

        return kwargs

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        drug = get_object_or_404(models.Drug, pk=self.kwargs['pk'])
        dispense = form.save(commit=False)

        # Dispense
        can_dispense = drug.can_dispense(dispense.dispense)
        if can_dispense:
            drug.dispense(dispense.dispense)
        else:
            return HttpResponseNotFound('<h1>Cannot dispense more drugs than in stock!</h1>')

        # Assign author and author type
        dispense.author = self.request.user
        dispense.author_type = get_active_role(self.request)
        dispense.patient = pt
        dispense.drug = drug

        dispense.save()
        form.save_m2m()

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
