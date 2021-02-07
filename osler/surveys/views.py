from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse

from osler.surveys.models import Survey


def test(request):
    return HttpResponse("survey test page")


class SurveyTemplateListView(generic.ListView):
    model = Survey
