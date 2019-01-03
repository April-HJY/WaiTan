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

def CampaignPage(request):
    template = loader.get_template('campaigns.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 

@csrf_exempt
def SaveCampaign(request):
    try:
        params = request.POST
        Log("SaveCampaign params: %s" % params, "local", "0.0.0.0", "DEBUG")
        update_id = params.get('id', None)
        start=params.get('start_date', None)
        end=params.get('end_date', None)
        updated=datetime.datetime.now()
        code = params.get('code')
        cname = params.get('cname')
        remark = params.get('remark')
        balance = params.get('balance', 0)
        url = params.get('url')
        if update_id:
            campaign = Campaign.objects.get(ID=update_id)
            campaign.Code = code
            campaign.CName = cname
            campaign.Balance = balance
            campaign.Updated = updated
            campaign.StartDate = start
            campaign.EndDate = end
            campaign.Remark = remark
            campaign.URL = url
            campaign.save()
        else:
            campaign = Campaign(Code=code, CName=cname, Balance=balance, Updated=updated, StartDate=start, EndDate=end, Remark=remark, URL = url)
            campaign.save()
        return HttpResponse('ok')
    except Exception,e:
        Log("SaveCampaign error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def DeleteCampaign(request):
    try:
        params = request.POST
        Log("SaveCampaign params: %s" % params, "local", "0.0.0.0", "DEBUG")
        delete_id = params.get('id', None)
        
        if delete_id:
            campaign = Campaign.objects.get(ID=delete_id)
            campaign.delete()

        return HttpResponse('ok')
    except Exception,e:
        Log("SaveCampaign error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
def GetCampaigns(request):
    try:
        updateVar('Campaign')
        Log("GetCampaigns ", "local", "0.0.0.0", "DEBUG")
        params = request.GET
        offset=0
        limit=10
        
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        
        campaigns = getVar('Campaign')
        page = int(offset/limit + 1)
        
        total = len(campaigns)
        res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        while i < last:
            campaign = campaigns[i]
            c_url = "%s?campaign=%s" % (campaign.URL, campaign.Code)
            show_url = "<a href='javascript:show_url(\"%s\")'>显示</a>" % c_url
            update = "<a href='javascript:update_campaign(%d)'>修改</a>" % campaign.ID
            copy = "<a href='javascript:copy_campaign(%d)'>复制</a>" % campaign.ID
            delete = "<a href='javascript:delete_campaign(%d)'>删除</a>" % campaign.ID
            balance = str(decimal.Decimal(campaign.Balance).quantize(decimal.Decimal('0.00')))
            startDate = None
            if campaign.StartDate:
                startDate = campaign.StartDate.strftime('%Y-%m-%d')
            endDate = None
            if campaign.EndDate:
                endDate = campaign.EndDate.strftime('%Y-%m-%d')
            res.append({"ID":campaign.ID, 'Code': campaign.Code, 'CName': campaign.CName, 'Balance':balance, 'StartDate':startDate, 'EndDate':endDate, 
                        'Status':'投放中', "URL":campaign.URL, "Remark":campaign.Remark, "Show_URL":show_url, "Update":update, "Copy":copy, "Delete":delete})
            i=i+1
        obj = {
            "page":page,
            "rows":res,
            "total":total
        }
        
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("GetCampaigns error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')


