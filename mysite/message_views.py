#coding: utf-8
from __future__ import division  
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.http import *
from utils import *
from django.views.decorators.csrf import csrf_exempt  
from itertools import *
from utils2 import *
from mem_db_sync import *
import urllib
import urllib2
import json
import httplib
from django.db.models import Q

        
def TagPage(request):
    template = loader.get_template('messageview.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))


def TelMessagePage(request):
    template = loader.get_template('telMessagePage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 


def GetMessages(request):
    messages = MessageLog.objects.all()
    res = []
    for message in messages:
        res.append({"ID":message.ID, "MsgType":message.MsgType, "Content": message.Content, "Result": message.Result})
    return HttpResponse(json.dumps(res))




    
