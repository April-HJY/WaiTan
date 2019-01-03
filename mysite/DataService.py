#coding: utf-8
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
import mimetypes

@csrf_exempt       
def updateSession(request):
    	Log("updateSession")
        try:
            if request.method == 'POST': 
                
                params = request.POST
                
                for key in params.keys():
                    request.session[key] = params[key]
                    Log("Key:%s, Value:%s" % (key, params[key] ))

            return HttpResponse("OK")
        except Exception, e:
            Log("Error:%s"%e)