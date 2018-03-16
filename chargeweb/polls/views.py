from django.shortcuts import get_object_or_404, render
from time import sleep

# Create your views here.
from django.http import HttpResponse
from .models import Question
from django.template import loader

POWER_LIMIT_FILENAME = '../pwr.txt'

def index(request):
    return HttpResponse("index")
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, charge_time):
    #Perform file IO
    minutes = int(charge_time) * 60
    try:
        with open(POWER_LIMIT_FILENAME, 'w') as f:
            f.write("%i" % minutes)
        f.closed
    except:
        sleep(2)	#Waiting 2 sec should be way enough to be able to write
        with open(POWER_LIMIT_FILENAME, 'w') as f:
            f.write("%i" % minutes)
        f.closed
    return HttpResponse("Charge is limited to  %s hour(s). (%.1f kWh)" % (charge_time, (minutes*3.7)/60))
