from __future__ import unicode_literals
from builtins import object
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from . import models


class BaseFollowup(ModelForm):
    '''The base class for followup forms'''
    class Meta(object):
        abstract = True
        model = models.Followup
        exclude = []

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('followup_close', 'Submit and Close Action', css_class = 'btn btn-warning'))
        self.helper.add_input(Submit('followup_create', 'Submit and Create Action', css_class = 'btn btn-info'))
        super(BaseFollowup, self).__init__(*args, **kwargs)


class ActionItemFollowup(BaseFollowup):
    class Meta(object):
        model = models.ActionItemFollowup
        exclude = ['patient', 'author', 'author_type','action_item']
