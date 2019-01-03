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
import decimal

def ChannelPage(request):
    template = loader.get_template('channelpage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 


def GetChannelsAndDistributors(request):
    try:
        params = request.GET
        res = []
        condition = params.get('condition')
        if condition != 'channel' and condition != 'distributor':
            condition = "channel;distributor"
        if 'channel' in condition:
            channelDic = GetChannelRemarkDic()
            for key in channelDic:
                #if key != 1:
                    res.append({"Name":channelDic[key], "Key": key})
        if 'distributor' in condition:
            distributors = TradeInfo.objects.values('DistributorName').distinct()
            for distributor in distributors:
                if distributor['DistributorName']:
                    res.append({"Name":distributor['DistributorName'], "Key": distributor['DistributorName']})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetChannelsAndDistributors error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetChannelsWithEditable(request):
    try:
        updateVar("Channel")
        params = request.GET
        res = []
        channels = getVar("Channel")
        for channel in channels:
            edit = ''
            #Log("GetChannelsWithEditable edit:%d"%channel.Editable, "local", "0.0.0.0", "DEBUG")
            if int(channel.Editable)==1:
                edit = "<a href='javascript:delete_channel(%d)'>删除</a>" % channel.ID
            res.append({"Code":channel.Name, "Name":channel.Remark, "ID": channel.ID, "Edit":edit})
        #Log("GetChannelsWithEditable res:%s"%res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetChannelsWithEditable error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    

@csrf_exempt
def SaveChannel(request):
    try:
        params = request.POST
        Log("SaveChannel params: %s" % params, "local", "0.0.0.0", "DEBUG")
        update_id = params.get('id', None)
        code = params.get('code')
        cname = params.get('cname')
        if update_id:
            channel = Channel.objects.get(ID=update_id)
            channel.Name = code
            channel.Remark = cname
            channel.save()
        else:
            channel = Channel(Name=code, Remark=cname, Editable=1)
            channel.save()
        updateVar("Channel")
        return HttpResponse('ok')
    except Exception,e:
        Log("SaveChannel error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def DeleteChannel(request):
    try:
        params = request.POST
        Log("DeleteChannel params: %s" % params, "local", "0.0.0.0", "DEBUG")
        delete_id = params.get('id', None)
        
        if delete_id:
            channel = Channel.objects.get(ID=delete_id)
            if channel.Editable == 1:
                channel.delete()
            else:
                HttpResponse('不可删除')

        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteChannel error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
