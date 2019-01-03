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
from django.db import transaction
import wxAccountInterface

OVERTIMEDAYS = 365
    
def UpdatePointToUser(wxuser_id, point, object_type='', object_id=0, reason=''):
    try:
        #Log("UpdatePointToUser", "local", "0.0.0.0", "DEBUG")
        detail = UserPointDetail.objects.filter(wxUserID = wxuser_id, Points = point, ObjectType = object_type, ObjectID = object_id, Reason = reason)
        if detail:
            #Log("UpdatePointToUser already update:%d %d %s %d %s" % (wxuser_id, point, object_type, object_id, reason), "local", "0.0.0.0", "DEBUG")
            return 'already update'
        
        with transaction.commit_on_success():
            detail = UserPointDetail(wxUserID = wxuser_id, Points = point, ObjectType = object_type, ObjectID = object_id, Reason = reason)
            detail.save()
            wxuser = wxUser.objects.get(ID=wxuser_id)
            wxuser.Points += point
            wxuser.save()
        return 'ok'
    except Exception,e:
        Log("UpdatePointToUser error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return e
    
    
def GetUserPoints(openid):
    try:
        wxuser = wxUser.objects.get(openID = openid)
        return wxuser.Points
    except Exception,e:
        Log("Point GetUserPoints error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return 0
    
    
def GetUserPointDetails(openid):
    try:
        wxuser = wxUser.objects.get(openID = openid)
        details = UserPointDetail.objects.values("Reason","Points","Created").filter(wxUserID = wxuser.ID).order_by("-ID")
        detail_list = []
        for detail in details:
            reason = detail['Reason']
            if reason == "分销":
                reason = "分享得奖学金"
            elif reason == "购买":
                reason = "购课得奖学金"
            elif reason == "新用户":
                reason = "新用户专享奖学金"
            elif reason == "消费":
                reason = "购课消费"
            points = detail['Points']
            created = detail['Created'].strftime("%Y-%m-%d  %H:%M:%S")
            detail_list.append({"reason": reason, "points":points, "created":created})
        return detail_list
    except Exception,e:
        Log("Point GetUserPointDetails error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return []
    
    
def ClearOvertimePoints(request):
    try:
        appid = 'wxf11978168e04aba2'
        wxusers = wxUser.objects.values('ID').filter(SourceAccount = appid)
        queue = TaskQueue('queue_name')
        for user in wxusers:
            task_url = "clearuserovertimepoints/"
            paraDic = {
                "wxuser_id":user['ID']
            }
            queue.add(Task(task_url, json.dumps(paraDic) ,delay=2))
        return HttpResponse('ok')
    except Exception,e:
        Log("Point ClearOvertimePoints error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def ClearUserOvertimePoints(request):
    try:
        overtime_days = OVERTIMEDAYS
        params = json.loads(request.raw_post_data)
        wxuser_id = int(params.get('wxuser_id',0))
        Log("Point ClearUserOvertimePoints %d" % wxuser_id,"local", "0.0.0.0", "DEBUG")
        overtime_date = (datetime.datetime.now() - datetime.timedelta(days = overtime_days)).strftime("%Y-%m-%d 00:00:00")
        #point_details = UserPointDetail.objects.filter(Created__lt=overtime_date, Points__gte=0, IsHandled=0)
        minus_details = UserPointDetail.objects.filter(wxUserID=wxuser_id, Points__lte=0, IsHandled=0)
        if minus_details:
            minus_points = 0
            point_details = UserPointDetail.objects.filter(wxUserID=wxuser_id, Points__gte=0, IsHandled=0)
            for detail in minus_details:
                minus_points += detail.Points
                detail.IsHandled = 1
                detail.save()
            for detail in point_details:
                if minus_points < 0:
                    minus_points += detail.Points
                    if minus_points <= 0:
                        detail.IsHandled = 1
                        detail.SpentPoints = detail.Points
                        detail.save()
                    else:
                        detail.SpentPoints = detail.Points - minus_points
                        detail.save()
        overtimepoint_details = UserPointDetail.objects.filter(wxUserID=wxuser_id, Created__lt=overtime_date, IsHandled=0)
        overtimepoint = 0
        for detail in overtimepoint_details:
            overtimepoint += detail.Points - detail.SpentPoints
            detail.SpentPoints = detail.Points
            detail.IsHandled = 1
            detail.save()
        if overtimepoint >0:
            UpdatePointToUser(wxuser_id, -overtimepoint, object_type='', object_id=0, reason='积分过期')
            Log("Point ClearUserOvertimePoints userid: %d;  points: %d" % (wxuser_id,overtimepoint), "local", "0.0.0.0", "DEBUG")
        return HttpResponse('ok')
    except Exception,e:
        Log("Point ClearUserOvertimePoints error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def SendOvertimeMsg(request):
    try:
        appid = 'wxf11978168e04aba2'
        wxusers = wxUser.objects.values('ID').filter(SourceAccount = appid)
        queue = TaskQueue('queue_name')
        for user in wxusers:
            task_url = "senduserovertimemessage/"
            paraDic = {
                "wxuser_id":user['ID']
            }
            queue.add(Task(task_url, json.dumps(paraDic) ,delay=2))
        return HttpResponse('ok')
    except Exception,e:
        Log("Point SendOvertimeMsg error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def SendUserOvertimeMsg(request):
    try:
        appid = "wx457b9d0e6f93d1c5"
        overtime_days1 = OVERTIMEDAYS - 7
        overtime_days2 = OVERTIMEDAYS - 30
        params = json.loads(request.raw_post_data)
        #params = request.GET
        wxuser_id = int(params.get('wxuser_id',0))
        overtime_date = (datetime.datetime.now() - datetime.timedelta(days = overtime_days1)).strftime("%Y-%m-%d 00:00:00")
        overtimepoint = 0
        overtimepoint_details = UserPointDetail.objects.filter(wxUserID=wxuser_id, Created__lt=overtime_date, IsHandled=0)
        if overtimepoint_details:
            for detail in overtimepoint_details:
                overtimepoint += detail.Points - detail.SpentPoints
            if overtimepoint >0:
                wxuser = wxUser.objects.get(ID=wxuser_id)
                wxserviceuser = wxUser.objects.filter(SourceAccount=appid, unionID=wxuser.unionID)
                if wxserviceuser:
                    wxObj = wxAccountInterface.wxAccountInterface(appid)
                    wxObj.SendPointOvertimeRemindTemplate(wxserviceuser[0].Name,overtimepoint,7,wxserviceuser[0].openID)
                Send106txtTelMsg(wxuser.Mobile, "【外滩教育】尊敬的外滩教育小主，您有%d奖学金将于7天内过期，现外滩教育推出了系列精品优惠好课，您可以在小程序中查看奖学金情况。奖学金购课可以抵现哦，赶快来看看吧～" % overtimepoint, 0)
                Log("Point SendUserOvertimeMsg userid:7 %d;  points: %d" % (wxuser_id,overtimepoint), "local", "0.0.0.0", "DEBUG")
        else:
            overtime_date = (datetime.datetime.now() - datetime.timedelta(days = overtime_days2)).strftime("%Y-%m-%d 00:00:00")
            overtimepoint_details = UserPointDetail.objects.filter(wxUserID=wxuser_id, Created__lt=overtime_date, IsHandled=0)
            for detail in overtimepoint_details:
                overtimepoint += detail.Points - detail.SpentPoints
            if overtimepoint >0:
                wxuser = wxUser.objects.get(ID=wxuser_id)
                wxserviceuser = wxUser.objects.filter(SourceAccount=appid, unionID=wxuser.unionID)
                if wxserviceuser:
                    wxObj = wxAccountInterface.wxAccountInterface(appid)
                    wxObj.SendPointOvertimeRemindTemplate(wxserviceuser[0].Name,overtimepoint,30,wxserviceuser[0].openID)
                Send106txtTelMsg(wxuser.Mobile, "【外滩教育】尊敬的外滩教育小主，您有%d奖学金将于30天内过期，现外滩教育推出了系列精品优惠好课，您可以在小程序中查看奖学金情况。奖学金购课可以抵现哦，赶快来看看吧～" % overtimepoint, 0)
                Log("Point SendUserOvertimeMsg userid:30 %d;  points: %d" % (wxuser_id,overtimepoint), "local", "0.0.0.0", "DEBUG")
        return HttpResponse('ok')
    except Exception,e:
        Log("Point SendUserOvertimeMsg error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
    