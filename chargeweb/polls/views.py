from django.shortcuts import get_object_or_404, render
from time import sleep
import subprocess
import json

# Create your views here.
from django.http import HttpResponse
from .models import Question
from django.template import loader

POWER_LIMIT_FILENAME = '../pwr.txt'
LOG_FILENAME = '../progress.log'
STATUS_FILENAME = '../status.txt'

def index(request):
    logtext = subprocess.run(['grep', '-v', 'DEBUG', LOG_FILENAME], stdout=subprocess.PIPE).stdout.decode('utf-8')

    #truncate the log if its big
    TRUNCKLIMIT = 2000
    if (TRUNCKLIMIT<len(logtext)):
        logtext = logtext[-TRUNCKLIMIT:]
        offset = logtext.find('\n')
        logtext = logtext[offset:]
        
    with open(STATUS_FILENAME) as json_file:  
        data = json.load(json_file)

        if (data['charging']):
            data['charging'] = "CHARGING"
        else:
            data['charging'] = ""

        if (data['connected']):
            data['connected'] = "CONNECTED"
        else:
            data['connected'] = ""

        if (data['chargeEnabled']):
            data['chargeEnabled'] = "ALLOWED"
        else:
            data['chargeEnabled'] = "NOT ALLOWED"

        if (data['button']):
            data['button'] = "ACTIVATED"
        else:
            data['button'] = "NOT ACTIVATED"

        if (1000000<data['limitRemaining']):
            data['limitRemaining'] = "-"

#    print(data)

    return render(request, 'polls/index.html', {'logtext': logtext, 'status': data})

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, charge_time):
    #Perform file IO
    minutes = int(charge_time)
    if (1000000<charge_time):
        minutes = 1000000000
        
    try:
        with open(POWER_LIMIT_FILENAME, 'w') as f:
            f.write("%i" % minutes)
        f.closed
    except:
        sleep(2)	#Waiting 2 sec should be way enough to be able to write
        with open(POWER_LIMIT_FILENAME, 'w') as f:
            f.write("%i" % minutes)
        f.closed
    if (1000000<charge_time):
        return HttpResponse("Charge is unlimited")
    else:
        return HttpResponse("Charge is limited to  %s hour(s). (%.1f kWh)" % (charge_time/60, (minutes*3.7)/60))
        
