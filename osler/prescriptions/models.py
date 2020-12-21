from django.db import models
from django import forms
from osler.inventory.models import Drug
# current plan is to just make each attribute a separate model and then 
class PrescriptionName(models.Model):
    # name = PrescritionModelField()
    name = models.ForeignKey(Drug, on_delete=models.PROTECT)
    def __str__(self):
        return self.name()


class PrescriptionDose(models.Model):
    # name = PrescritionModelField()
    dose = dose = models.TextField(verbose_name="HPI", blank=True)

    def __str__(self):
        return self.name()

       
    route = models.TextField(verbose_name="HPI", blank=True)
    freq = models.TextField(verbose_name="HPI", blank=True)


# class Prescription(forms.fields.MultiValueField):
#     def __init__(self, **kwargs):
#         # Define one message for all fields.
#         error_messages = {
#             'incomplete': 'Enter a country calling code and a phone number.',
#         }
#         # Or define a different message for each field.
#         fields = (
#             models.CharField(
#                 error_messages={'incomplete': 'Enter a country calling code.'},
#             ),
#             models.CharField(
#                 error_messages={'incomplete': 'Enter a phone number.'},
#             ),
#             models.CharField(
#                 required=False,
#             ),
#         )
#         super().__init__(
#             error_messages=error_messages, fields=fields,
#             require_all_fields=False, **kwargs
#         )
# class PrescriptionWidget(forms.MultiWidget):
#     def __init__(self, *args, **kwargs):
        
#         self.widgets = [
#             forms.TextInput(),
#             forms.TextInput()
#         ]
#         super(PrescriptionWidget, self).__init__(*args, **kwargs, widgets=self.widgets)

#     def decompress(self, value):
#         if value:
#             return value.split(' ')
#         return [None, None]


# class PrescriptionField(forms.MultiValueField):
#     widget = PrescriptionWidget

#     def __init__(self, *args, **kwargs):
       
#         fields = (
#             models.CharField(),
#             models.CharField()
#         )
#         super(PrescriptionField, self).__init__(*args, **kwargs, fields=fields)

#     def compress(self, data_list):
#         return ' '.join(data_list)


# class PrescritionModelField(models.Field):

#     def formfield(self, **kwargs):
#         defaults = {'form_class': PrescriptionField}
#         defaults.update(kwargs)
#         return super(PrescritionModelField, self).formfield(**defaults)

#     def get_internal_type(self):
#         return 'TextField'





