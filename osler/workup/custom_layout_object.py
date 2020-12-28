from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from django.shortcuts import render
from django.template.loader import render_to_string
from osler.prescriptions.forms import PrescriptionFormSet


class Formset(LayoutObject):
    template = "prescriptions/prescription_formset.html"

    def __init__(self, formset_name_in_context, template=None):
        self.formset_name_in_context = formset_name_in_context
        # print(formset_name_in_context)
        self.fields = []
        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        '''Render formset passed in the Formset Layout object argument by referencing a dictionary of existing formsets'''
        formsets = {
            'PrescriptionFormSet': PrescriptionFormSet
        }
        return render_to_string(self.template, {'formset': formsets[self.formset_name_in_context]})
