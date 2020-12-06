from functools import reduce
from osler.core.models import (Patient, Encounter)

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from .models import Lab, LabType  
from .forms import LabCreationForm, MeasurementsCreationForm
from .utils import get_measurements_from_lab,get_measurementtypes_from_labtype

from django.utils import timezone
from datetime import datetime, timedelta

from django.utils.decorators import method_decorator
from osler.users.utils import get_active_role, group_has_perm
from osler.users.decorators import active_permission_required
from osler.core.views import get_clindates


class LabListView(ListView):
    """
    List all labs in a list
    """
    model = Lab
    template_name = 'labs/lab_all.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        context['pt'] = self.pt
        context['labs'] = Lab.objects.filter(patient=self.kwargs['pt_id'])
        active_role = get_active_role(self.request)
        for perm in ['add_lab']:
            context[perm] = group_has_perm(active_role, 'labs.%s' % perm)
        return context


class LabDetailView(DetailView):
    """
    List all measurement values to one lab
    """
    model = Lab
    context_object_name = 'lab'
    template_name = 'labs/lab_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LabDetailView,self).get_context_data(**kwargs)
        self.lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
        context['lab'] = self.lab
        context['pt'] = self.lab.patient
        measurement_list = get_measurements_from_lab(self.lab.id)
        context['measurement_list'] = measurement_list
        active_role = get_active_role(self.request)
        for perm in ['change_lab']:
            context[perm] = group_has_perm(active_role, 'labs.%s' % perm)
        return context


@method_decorator(active_permission_required('labs.add_lab', raise_exception=True), name='dispatch')
class LabCreate(FormView):
    """
    Lab create view (part 1) where the user chooses a lab type
    """
    template_name = 'labs/lab_create.html'
    form_class = LabCreationForm


    def get_form_kwargs(self):
        kwargs = super(LabCreate, self).get_form_kwargs()

        pt_id = self.kwargs['pt_id']
        kwargs['pt'] = get_object_or_404(Patient, pk=pt_id)

        return kwargs

    def form_valid(self, form):
        pt_id = self.kwargs['pt_id']
        new_lab = form.save(commit=False)
        new_lab_type = get_object_or_404(LabType, name=new_lab.lab_type)

        return redirect(reverse("labs:new-full-lab", args=(pt_id,new_lab_type.id,)))


@method_decorator(active_permission_required('labs.add_lab', raise_exception=True), name='dispatch')
class MeasurementsCreate(FormView):
    """
    Lab create view (part 2) where the user fills in all measurement values associated with the choosen lab type
    """
    template_name = 'labs/lab_create.html'
    form_class = MeasurementsCreationForm

    def get_form_kwargs(self):
        kwargs = super(MeasurementsCreate, self).get_form_kwargs()

        pt_id = self.kwargs['pt_id']
        lab_type_id = self.kwargs['lab_type_id']
        kwargs['pt'] = get_object_or_404(Patient, pk=pt_id)
        kwargs['new_lab_type'] = get_object_or_404(LabType, pk=lab_type_id)

        return kwargs

    def get_initial(self):
        initial = super(MeasurementsCreate, self).get_initial()

        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        clinic_day = get_clindates().first()
        #if encounter for today's clinic day, select as initial
        if Encounter.objects.filter(patient=pt, clinic_day=clinic_day).exists():
            initial['encounter'] = Encounter.objects.get(patient=pt, clinic_day=clinic_day)
        
        return initial

    def form_valid(self, form):
        pt_id = self.kwargs['pt_id']
        form.save()

        return redirect(reverse("labs:all-labs-table", args=(pt_id,)))


@method_decorator(active_permission_required('labs.change_lab', raise_exception=True), name='dispatch')
class MeasurementsEdit(FormView):
    """
    Lab edit view
    Same view as lab create view (part 2) but with a form prepopulated with existing values of the lab
    """
    template_name = 'labs/lab_edit.html'
    form_class = MeasurementsCreationForm

    def get_form_kwargs(self):
        kwargs = super(MeasurementsEdit, self).get_form_kwargs()

        lab_id = self.kwargs['pk']
        lab = get_object_or_404(Lab, pk=lab_id)
        kwargs['lab_pk'] = lab_id
        kwargs['pt'] = lab.patient
        kwargs['new_lab_type'] = lab.lab_type

        return kwargs


    def form_valid(self, form):
        lab_id = self.kwargs['pk']
        form.save(lab_pk=lab_id)

        return redirect(reverse("labs:lab-detail", args=(lab_id,)))


def view_all_as_table(request,pt_id,month_range=6):
    """
    Lab table view with recent labs
    A table with rows as measurement values and columns as labs
    Displays recent labs
    """
    if request.method == 'GET' and 'select' in request.GET:
        month_range = int(request.GET['select'])

    # Get qs for the patient
    pt = get_object_or_404(Patient, id=pt_id)
    lab_types = list(LabType.objects.all())

    to_tz = timezone.get_default_timezone()
    time_threshold = datetime.now(to_tz) - timedelta(days=month_range*31)
    lab_qs = Lab.objects.filter(patient=pt_id, lab_time__gt=time_threshold)
    lab_days = sorted([lab.get_day() for lab in lab_qs], reverse=True)
    unique_lab_days=reduce(lambda l, x: l if x in l else l+[x], lab_days, [])

    listed_lab_days = unique_lab_days[:]
    n_days = len(listed_lab_days)

    # Initiate empty table
    # width = # of labs
    # height = # of measurement types

    table_header = ['','Reference']
    col_header_len = len(table_header)
    table_header += [ str(x) for x in listed_lab_days ]
    table_content = []
    sorted_measure_types = []
    dup_lab_bool = False

    for t_lab_type in lab_types:
        m_types = get_measurementtypes_from_labtype(t_lab_type.id)
        table_content.append([table_header[:]])
        table_content[-1][0][0] = ('Lab Category: '+str(t_lab_type))
        sorted_measure_types.append([])
        for mt in m_types:
            table_content[-1].append(([mt, mt.get_ref()] + ['']*n_days))
            sorted_measure_types[-1].append(mt)


    # Fill in entries
    for t_lab in lab_qs.reverse():
        if (not (t_lab.get_day() in listed_lab_days)):
            continue
        measurements = get_measurements_from_lab(t_lab.id)
        col_index = listed_lab_days.index(t_lab.get_day()) + col_header_len
        for m in measurements:
            section_index = lab_types.index(t_lab.lab_type)
            m_type = m.measurement_type
            row_index = (sorted_measure_types[section_index]).index(m_type)
            current_value = table_content[section_index][row_index+1][col_index]
            if current_value=='':
                table_content[section_index][row_index+1][col_index] = m
            else:
                table_content[section_index][row_index+1][col_index] = m
                table_content[section_index][0][col_index] += '*'
                dup_lab_bool = True

    qs = {'patient':pt, 
          'table_content': table_content,
          'add_lab': group_has_perm(get_active_role(request), 'labs.add_lab'),
          'no_lab_bool':len(lab_qs)==0,
          'dup_lab_bool': dup_lab_bool}

    return render(request, 'labs/lab_all_table.html', qs)