from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from osler.users.utils import get_active_role
from osler.surveys.models import Survey, Question, Response, Answer
from osler.core.models import Patient, Encounter


def create(request):
    '''create a new survey, and redirect to editing it'''
    new_survey = Survey(title="Untitled Survey")
    new_survey.save()
    return redirect('surveys:edit', id=new_survey.id)


class SurveyListView(generic.ListView):
    model = Survey


class AllResponsesListView(generic.ListView):
    '''list view for responses from all surveys'''
    model = Response

    def get_queryset(self):
        pt_id = self.request.GET.get('pt_id', None)
        if pt_id is not None:
            encounters = Encounter.objects.filter(patient_id=pt_id)
            return Response.objects.filter(encounter__in=encounters)
        return Response.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pt_id = self.request.GET.get('pt_id', None)
        if pt_id is not None:
            context['patient'] = Patient.objects.get(id=pt_id)
        return context


class ResponsesListView(generic.ListView):
    '''list view for responses from a specific survey'''
    model = Response

    def get_queryset(self):
        return Survey.objects.get(id=self.kwargs['id']).responses.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add survey to context
        context['survey'] = Survey.objects.get(id=self.kwargs['id'])
        return context

# surveys is a list of surveys


def filteredSurveys(request, pid):
    incomplete_surveys = Survey.get_incomplete_surveys(pid)
    patient = Patient.objects.get(pk=pid)
    context = {'surveys': incomplete_surveys, 'patient': patient}
    return render(request, 'surveys/filtered_surveys_list.html', context)


def response(request, id):
    response = Response.objects.get(id=id)
    # get answers into a dict of lists
    answer_dict = {}
    for ans in response.answers.all():
        qid = ans.question.question
        if qid not in answer_dict.keys():
            answer_dict[qid] = [ans.text]
        else:
            answer_dict[qid] = answer_dict[qid] + [ans.text]
    ctx = {'response': response, 'answer_dict': answer_dict}
    return render(request, 'surveys/response_detail.html', ctx)


def fill(request, pid, id):
    survey = Survey.objects.get(id=id)
    ctx = {'survey': survey,
           'QuestionType': Question.QuestionType,
           'pid': pid
           }

    patient = get_object_or_404(Patient, id=pid)

    active_role = get_active_role(request)
    can_activate = patient.group_can_activate(active_role)

    if not patient.get_status().is_active and not can_activate:
        messages.add_message(request, messages.ERROR,
                             'You are trying to survey an inactive patient, but do not have permission to activate this patient')
        return redirect('surveys:filtered_surveys', pid=pid)
    return render(request, 'surveys/fill.html', ctx)


def view(request, id):
    survey = Survey.objects.get(id=id)
    ctx = {'survey': survey,
           'QuestionType': Question.QuestionType,
           'readonly': True
           }

    return render(request, 'surveys/fill.html', ctx)

# TODO: for response object check if there is an encounter for patient, if not create encounter


def submit(request, pid, id):
    '''recieves data from a survey fill and creates a response object'''
    if request.method != "POST":
        return redirect('surveys:fill', id=id)

    survey = get_object_or_404(Survey, id=id)
    patient = get_object_or_404(Patient, id=pid)

    active_role = get_active_role(request)
    can_activate = patient.group_can_activate(active_role)

    # Check for patient status, if active use encounter property
    # if not active toggle status then get encounter
    encounter = None
    if patient.get_status().is_active:
        encounter = patient.last_encounter()
    else:
        if can_activate:
            patient.toggle_active_status(request.user, active_role)
            encounter = patient.last_encounter()
        else:
            # FIXME is this the best way to raise error?
            raise PermissionDenied

    response = Response(survey=survey)
    response.author = request.user
    response.author_role = get_active_role(request)
    response.encounter = encounter
    response.save()

    for question_id in request.POST:
        if question_id == "csrfmiddlewaretoken":
            continue
        if not question_id.isnumeric() or survey.questions.filter(id=question_id).count() == 0:
            # a question was present that is not in the survey - abort
            response.delete()
            messages.error(request, 'Error: Form Invalid')
            return redirect('surveys:fill', id=id)

        for ans in request.POST.getlist(question_id):
            if ans == '':
                continue
            q = Question.objects.get(id=question_id)
            answer = Answer(question=q, text=ans, response=response)
            answer.save()

    messages.success(request, "Form Submitted Sucessfully.")
    # TODO: change redirect to individual response view
    return redirect('surveys:filtered_surveys', pid=pid)
