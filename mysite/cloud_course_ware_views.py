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
import wxAccountInterface
import talk_cloud_interface

    
def coursewarepage(request):
        template = loader.get_template('coursewarepage.html')
        context = RequestContext(request, {"Info":mc.get("ticket")})
        return HttpResponse(template.render(context))

    
@csrf_exempt
def UploadFile(request):
    try:
        params = request.POST
        #Log("UploadFile params: %s" % params, Type="DEBUG")
        if request.FILES.has_key("filedata"):
            option = params.get('is_dynm', '')
            classroom_serial = int(params.get('classroom_serial', 0))
            is_open = 1
            if classroom_serial:
                is_open = 0
            is_dynm = 0
            if str(option) == 'on':
                is_dynm = 1 
                
            #Log("UploadFile %d" % is_dynm, Type="DEBUG")
            ware_file = request.FILES["filedata"]
            res = talk_cloud_interface.UploadWare(ware_file,is_open,is_dynm, classroom_serial)
            if res['result'] == 0:
                return HttpResponse('ok')
            else:
                return HttpResponse('失败')
        else:
            return HttpResponse('没找到文件')
    except Exception,e:
        Log("UploadFile error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def DeleteFile(request):
    try:
        Log("DeleteFile", Type="DEBUG")
        params = request.POST
        file_id = int(params.get('file_id', 0))
        res = talk_cloud_interface.DeleteWare(file_id)
        if res['result'] == 0:
            return HttpResponse('ok')
        else:
            return HttpResponse('失败')
    except Exception,e:
        Log("DeleteFile error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def ConnectFile(request):
    try:
        params = request.POST
        Log("ConnectFile params: %s" %params, Type="DEBUG")
        file_id = int(params.get('file_id', 0))
        classroom_serial = int(params.get('classroom_serial', 0))
        
        res = talk_cloud_interface.ConnectWare(file_id,classroom_serial)
        Log("ConnectFile res: %s" %res, Type="DEBUG")
        if res['result'] == 0:
            return HttpResponse('ok')
        else:
            return HttpResponse('失败')
    except Exception,e:
        Log("ConnectFile error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
    
def GetCourseWare(request):
    try:
        params = request.GET
        company_files = talk_cloud_interface.GetCompanyFiles()
        for company_file in company_files:
            company_file['edit'] = "<a href='javascript:delete_file(%d)'>删除</a>" % (int(company_file['fileid']))
        return HttpResponse(json.dumps(company_files))
    except Exception,e:
        Log("GetCourseWare error: %s" % e, Type="DEBUG")
        return HttpResponse(None)
    
    