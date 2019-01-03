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

def MainPage(request):
    template = loader.get_template('index.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 


def SalesStatisticsData(request):
    try:
        params = request.GET
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).order_by("PayTime")
        Log("SalesStatisticsData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    trades = trades.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    trades = trades.filter(DistributorName=channel)
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start =  datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end =  datetime.datetime.strptime(end, '%Y-%m-%d') +  datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)
        res=[]
        user_ids = trades.values("UserID").distinct()
        Log("SalesStatisticsData user_ids: %d" % len(user_ids), "local", "0.0.0.0", "DEBUG")
        users = User.objects.filter(ID__in=user_ids)
        new_users = users.filter(Created__gt=start, Created__lt=end)
        old_users = users.filter(Q(Created__lt=start) | Q(Created__gt=end))

        summary_user_count = 0
        summary_total_fee = 0
        summary_trade_count = 0
        if new_users:
            new_user_ids = new_users.values("ID")
            new_user_trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).filter(UserID__in=new_user_ids)#.countaggregate(Sum("Payment"))
            Log("SalesStatisticsData new_user_trade_count: %d" % len(new_user_trades), "local", "0.0.0.0", "DEBUG")
            new_user_count = len(new_users)
            summary_user_count += new_user_count
            new_user_trade_count = len(new_user_trades)
            summary_trade_count += new_user_trade_count
            new_user_trade_fee = new_user_trades.aggregate(Sum("Payment"))
            new_total_fee = new_user_trade_fee['Payment__sum']
            summary_total_fee += new_total_fee
            new_avg_trade_fee = new_total_fee / new_user_trade_count
            new_total_fee = decimal.Decimal(new_total_fee).quantize(decimal.Decimal('0.00'))
            new_avg_trade_count = new_user_trade_count * 1.0 / new_user_count
            new_avg_trade_count = decimal.Decimal(new_avg_trade_count).quantize(decimal.Decimal('0.00'))
            new_avg_trade_fee = decimal.Decimal(new_avg_trade_fee).quantize(decimal.Decimal('0.00'))
            res.append({"Name":"新用户", "Count":new_user_count, "TotalFee": str(new_total_fee), "AvgTradeCount":str(new_avg_trade_count), "AvgTradeFee":str(new_avg_trade_fee)})
        else:
            res.append({"Name":"新用户", "Count":0, "TotalFee": 0, "AvgTradeCount":0, "AvgTradeFee":0})
        
        Log("SalesStatisticsData res: %s" % res, "local", "0.0.0.0", "DEBUG")
        if old_users:
            old_user_ids = old_users.values("ID")
            old_user_trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).filter(UserID__in=old_user_ids)#.countaggregate(Sum("Payment"))
            old_user_count = len(old_users)
            summary_user_count += old_user_count
            old_user_trade_count = len(old_user_trades)
            summary_trade_count += old_user_trade_count
            old_user_trade_fee = old_user_trades.aggregate(Sum("Payment"))
            old_total_fee = old_user_trade_fee['Payment__sum']
            summary_total_fee += old_total_fee
            old_avg_trade_fee = old_total_fee / old_user_trade_count
            old_total_fee = decimal.Decimal(old_total_fee).quantize(decimal.Decimal('0.00'))
            old_avg_trade_count = old_user_trade_count * 1.0 / old_user_count
            old_avg_trade_count = decimal.Decimal(old_avg_trade_count).quantize(decimal.Decimal('0.00'))
            old_avg_trade_fee = decimal.Decimal(old_avg_trade_fee).quantize(decimal.Decimal('0.00'))
            res.append({"Name":"老用户", "Count":old_user_count, "TotalFee": str(old_total_fee), "AvgTradeCount":str(old_avg_trade_count), "AvgTradeFee":str(old_avg_trade_fee)})
        else:
            res.append({"Name":"老用户", "Count":0, "TotalFee": 0, "AvgTradeCount":0, "AvgTradeFee":0})
            
        if summary_user_count:
            summary_avg_trade_count = summary_trade_count * 1.0 / summary_user_count
            summary_avg_trade_fee = summary_total_fee/ summary_trade_count
            summary_total_fee = decimal.Decimal(summary_total_fee).quantize(decimal.Decimal('0.00'))
            summary_avg_trade_count = decimal.Decimal(summary_avg_trade_count).quantize(decimal.Decimal('0.00'))
            summary_avg_trade_fee = decimal.Decimal(summary_avg_trade_fee).quantize(decimal.Decimal('0.00'))
            res.append({"Name":"总计", "Count":summary_user_count, "TotalFee": str(summary_total_fee), "AvgTradeCount":str(summary_avg_trade_count), "AvgTradeFee":str(summary_avg_trade_fee)})
        else:
            res.append({"Name":"总计", "Count":0, "TotalFee": 0, "AvgTradeCount":0, "AvgTradeFee":0})
        
        Log("SalesStatisticsData res: %s" % res, "local", "0.0.0.0", "DEBUG")
        obj = {
            "page":1,
            "rows":res,
            "total":3
        }

        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("SalesStatisticsData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps([]))
    
    
def TradeCategoryRate(request):
    try:
        params = request.GET
        days = 30
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).order_by("PayTime")
        users = None
        Log("NewUserProvincePercentData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    trades = trades.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    trades = trades.filter(DistributorName=channel)
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start =  datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end =  datetime.datetime.strptime(end, '%Y-%m-%d') +  datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)
        data = []

        trade_list = trades.values('LessonCategoryID').annotate(count=Count('LessonCategoryID'), Sum=Sum('Payment'))
        cate_dic = GetCategoryDic()

        for trade in trade_list:
            if trade['LessonCategoryID']:
                data.append([cate_dic[trade['LessonCategoryID']],str(GetDecimal(trade['Sum']))])
        Log("TradeCategoryRate trade_list: %s" % trade_list, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(data))
    except Exception,e:
        Log("TradeCategoryRate error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps([]))
    

def NewUserProvincePercentData(request):
    try:
        params = request.GET
        days = 30
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).order_by("PayTime")
        users = None
        Log("NewUserProvincePercentData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    trades = trades.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    trades = trades.filter(DistributorName=channel)
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start =  datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
                users = User.objects.filter(Created__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end =  datetime.datetime.strptime(end, '%Y-%m-%d') +  datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
                users = users.filter(Created__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)
        data = []
        if users:
            user_ids = trades.values("UserID")
            user_areas = users.values("Province").filter(~Q(Province = '')).filter(ID__in=user_ids).annotate(Count('Province')).order_by("-Province__count")
            user_count = 0
            for area in user_areas:
                user_count += area['Province__count']
            
            for area in user_areas:
                percent = area['Province__count'] * 100.0 / user_count
                percent = decimal.Decimal(percent).quantize(decimal.Decimal('0.00'))
                data.append([area['Province'], str(percent)])

        return HttpResponse(json.dumps(data))
    except Exception,e:
        Log("NewUserProvincePercentData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps([]))


def UserProvincePercentData(request):
    try:
        params = request.GET
        days = 30
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).order_by("PayTime")
        #users = User.objects.filter(~Q(Province = '')).order_by("-Created")
        Log("UserProvincePercentData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    trades = trades.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    trades = trades.filter(DistributorName=channel)
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start =  datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end =  datetime.datetime.strptime(end, '%Y-%m-%d') +  datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)
        data = []

        user_ids = trades.values("UserID")
        user_areas = User.objects.values("Province").filter(~Q(Province = '')).filter(ID__in=user_ids).annotate(Count('Province')).order_by("-Province__count")
        user_count = 0
        for area in user_areas:
            user_count += area['Province__count']
            
        for area in user_areas:
            percent = area['Province__count'] * 100.0 / user_count
            percent = decimal.Decimal(percent).quantize(decimal.Decimal('0.00'))
            data.append([area['Province'], str(percent)])

        return HttpResponse(json.dumps(data))
    except Exception,e:
        Log("UserProvincePercentData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps([]))

def LessonTop10Data(request):
    try:
        params = request.GET
        days = 30
        start=None
        end=None
        lesson_id=None
        channel=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None))
        Log("LessonTop10Data params: %s" % params, "local", "0.0.0.0", "DEBUG")
        order_by = "count"
        if params.has_key('sortName') and params['sortName']:
            order_by = params['sortName']
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    trades = trades.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    trades = trades.filter(DistributorName=channel)
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end =  datetime.datetime.now() +  datetime.timedelta(days = 1)
        order_by = "-%s" % order_by
        trades = trades.values('Name','ChannelID','DistributorName').annotate(count=Count('Name'), fee=Sum('Payment')).order_by(order_by)

        total = len(trades)
        if total > 20:
            total = 20
        res = []
        channelDic = GetChannelRemarkDic()
        i = 0
        while i < total:
            trade = trades[i]
            channelRemark = channelDic[trade['ChannelID']]
            res.append({"Name": trade['Name'], "ChannelName": channelRemark, "DistributorName":trade['DistributorName'], "count": trade['count'], "fee": str(trade['fee'])})
            i += 1
        page = 1

        obj = {
            "page":page,
            "rows":res,
            "total":total
        }
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("LessonTop10Data error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')

def NewUserPercentData(request):
    try:
        params = request.GET
        days = 30
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).order_by("PayTime")
        Log("NewUserPercentData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    trades = trades.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    trades = trades.filter(DistributorName=channel)
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start =  datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end =  datetime.datetime.strptime(end, '%Y-%m-%d') +  datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)
        
        trades = trades.values("IsNewUserTrade")
        Log("NewUserPercentData len: %d" % len(trades), "local", "0.0.0.0", "DEBUG")
        data = []
        new_count = 0
        old_count = 0
        
        for trade in trades:
            if trade['IsNewUserTrade']:
                new_count += 1
            else:
                old_count += 1
        if new_count + old_count == 0:
            return HttpResponse(json.dumps([]))
        new_percent = new_count * 100.0 / (new_count + old_count)
        old_percent = old_count * 100.0 / (new_count + old_count)
        new_percent = decimal.Decimal(new_percent).quantize(decimal.Decimal('0.00'))
        old_percent = decimal.Decimal(old_percent).quantize(decimal.Decimal('0.00'))
        data.append(["首订订单", str(new_percent)])
        data.append(["复订订单", str(old_percent)])
    
        Log("NewUserPercentData data: %s" % data, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(data))
    except Exception,e:
        Log("NewUserPercentData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps([]))

def NewUserComparisonData(request):
    try:
        params = request.GET
        days = 30
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).order_by("PayTime")
        Log("NewUserComparisonData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    trades = trades.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    trades = trades.filter(DistributorName=channel)
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start =  datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end =  datetime.datetime.strptime(end, '%Y-%m-%d') +  datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)
        if start is not None:
            days = (end-start).days -1
            
        trades = trades.values('IsNewUserTrade','PayTime')
        total = len(trades)
        res = {}
        categories = []
        channelDic = GetChannelRemarkDic()
        for trade in trades:
            key = "老用户订单"
            if trade['IsNewUserTrade']:
                key = "新用户订单"

            if not res.has_key(key):
                res[key] = {}
                i = days
                while i >= 0:
                    date = (datetime.datetime.now() + datetime.timedelta(days = -i)).strftime('%Y-%m-%d') 
                    res[key][date] = 0
                    if date not in categories:
                        categories.append(date)
                    i -= 1
            if res[key].has_key(trade.PayTime.strftime('%Y-%m-%d')):
                res[key][trade['PayTime'].strftime('%Y-%m-%d')] += 1
        obj = {
            "categories":categories,
            "series":{}
        }
        for key in res:
            if not obj["series"].has_key(key):
                obj["series"][key] = []
            for cate in categories:
                obj["series"][key].append(res[key][cate])
            
        Log("NewUserComparisonData obj: %s" % obj, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("NewUserComparisonData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')

def ChannelClassPercentageData(request):
    try:
        params = request.GET
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None))
        Log("ChannelClassPercentageData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)

        trades = trades.values('ChannelID','TradeType','DistributorName')
        total = len(trades)
        res = {}
        channelDic = GetChannelRemarkDic()
        
        for trade in trades:
            channelRemark = channelDic[trade['ChannelID']]
            if not res.has_key(channelRemark):
                res[channelRemark] = {}
            if trade['TradeType'] == "BULK_PURCHASE":
                if not res[channelRemark].has_key(trade['DistributorName']):
                    res[channelRemark][trade['DistributorName']] = 1
                else:
                    res[channelRemark][trade['DistributorName']] += 1
            else:
                if not res[channelRemark].has_key(channelRemark):
                    res[channelRemark][channelRemark] = 1
                else:
                    res[channelRemark][channelRemark] += 1
        Log("ChannelClassPercentageData res: %s" % res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("ChannelClassPercentageData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')
    
    
def ChannelClassTimeLineData(request):
    try:
        params = request.GET
        days = 30
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None)).order_by("PayTime")
        Log("ChannelClassTimeLineData params: %s" % params, "local", "0.0.0.0", "DEBUG")
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                trades = trades.filter(PayTime__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(days = 1)
                trades = trades.filter(PayTime__lt=end)
            except Exception,e:
                end = datetime.datetime.now() + datetime.timedelta(days = 1)
        if start is not None:
            days = (end-start).days -1
        
        trades = trades.values('ChannelID','TradeType','DistributorName','PayTime')
        total = len(trades)
        res = {}
        categories = []
        channelDic = GetChannelRemarkDic()
        for trade in trades:
            channelRemark = channelDic[trade['ChannelID']]
            if trade['TradeType'] == "BULK_PURCHASE":
                channelRemark = trade['DistributorName']
            if not res.has_key(channelRemark):
                res[channelRemark] = {}
                i = days
                while i >= 0:
                    date = (datetime.datetime.now() + datetime.timedelta(days = -i)).strftime('%Y-%m-%d') 
                    res[channelRemark][date] = 0
                    if date not in categories:
                        categories.append(date)
                    i -= 1
            if res[channelRemark].has_key(trade['PayTime'].strftime('%Y-%m-%d')):
                res[channelRemark][trade['PayTime'].strftime('%Y-%m-%d')] += 1
        obj = {
            "categories":categories,
            "series":{}
        }
        for key in res:
            if not obj["series"].has_key(key):
                obj["series"][key] = []
            for cate in categories:
                obj["series"][key].append(res[key][cate])
            
        Log("ChannelClassTimeLineData obj: %s" % obj, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("ChannelClassTimeLineData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')

