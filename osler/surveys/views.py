from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from osler.users.utils import get_active_role
from osler.surveys.models import Survey, Question, Response, Answer
from osler.core.models import Patient


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


def filteredSurveys(request, id):
    incomplete_surveys = Survey.get_incomplete_surveys(id)
    context = {'surveys': incomplete_surveys}
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


def fill(request, id):
    survey = Survey.objects.get(id=id)
    ctx = {'survey': survey,
           'QuestionType': Question.QuestionType
           }

    return render(request, 'surveys/fill.html', ctx)


def view(request, id):
    survey = Survey.objects.get(id=id)
    ctx = {'survey': survey,
           'QuestionType': Question.QuestionType,
           'readonly': True
           }

    return render(request, 'surveys/fill.html', ctx)

# TODO: for response object check if there is an encounter for patient, if not create encounter


def submit(request, id):
    '''recieves data from a survey fill and creates a response object'''
    if request.method != "POST":
        return redirect('surveys:fill', id=id)

    survey = get_object_or_404(Survey, id=id)
    response = Response(survey=survey)
    response.author = request.user
    response.author_role = get_active_role(request)
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
    return redirect('surveys:responses', id=id)
