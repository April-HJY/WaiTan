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

def SalesPage(request):
    template = loader.get_template('sales.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 


def GetCategories(request):
    try:
        cates = LessonCategory.objects.values("ID","Name").all()
        res = []
        for cate in cates:
            res.append(cate)
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCategories error: %s" % e, Type="DEBUG")
        return HttpResponse(json.dumps([]))


def SalesStatisticsData(request):
    try:
        params = request.GET
        start=None
        end=None
        lesson_id=None
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None),~Q(Payment = 0), IsRefund=0).order_by("PayTime")
        Log("SalesStatisticsData params: %s" % params, "local", "0.0.0.0", "DEBUG")

        if params.has_key('category'):
            cate=params['category']
            if cate and cate != 'all':
                try:
                    cate=int(cate)
                    trades = trades.filter(LessonCategoryID=cate)
                except Exception,e:
                    cate = ''
                    
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('viewType') and params.get('viewType') != '':
            view_type = params['viewType']
            t = time.localtime(time.time())
            if view_type == 'daily':
                start =  datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d') 
                trades = trades.filter(PayTime__gt=start)
            elif view_type == 'weekly':
                start =  datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d 00:00:00'),'%Y-%m-%d %H:%M:%S') + datetime.timedelta(days = -(datetime.datetime.now().isoweekday()-1))
                trades = trades.filter(PayTime__gt=start)
            elif view_type == 'monthly':
                start =  datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-01 00:00:00'),'%Y-%m-%d %H:%M:%S')
                trades = trades.filter(PayTime__gt=start)
            end = datetime.datetime.now() + datetime.timedelta(days = 1)
        else:
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
        #users = User.objects.filter(ID__in=user_ids)
        new_user_ids = User.objects.values("ID").filter(ID__in=user_ids).filter(Created__gt=start, Created__lt=end)
        new_user_id = []
        for user_id in new_user_ids:
            new_user_id.append(user_id['ID'])
        old_user_ids = User.objects.values("ID").filter(ID__in=user_ids).filter(Q(Created__lt=start) | Q(Created__gt=end))
        old_user_id = []
        for user_id in old_user_ids:
            old_user_id.append(user_id['ID'])

        summary_user_count = 0
        summary_total_fee = 0
        summary_trade_count = 0
        
        if new_user_ids:
            new_user_trades = trades.values("Payment").filter(~Q(ThirdPartyID = None), UserID__in=new_user_id)#.countaggregate(Sum("Payment"))
            #new_user_trade_count = trades.filter(~Q(ThirdPartyID = None)).annotate(count=Count('ID'))[0]['count']
            #new_total_fee = trades.filter(~Q(ThirdPartyID = None), UserID__in=new_user_ids).annotate(fee=Sum('Payment'))[0]['fee']
            new_user_count = len(new_user_id)
            summary_user_count += new_user_count
            new_user_trade_count = len(new_user_trades)
            summary_trade_count += new_user_trade_count
            new_total_fee = 0
            for new_user_trade in new_user_trades:
                new_total_fee += new_user_trade['Payment']
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

        if old_user_ids:
            old_user_trades = trades.values("Payment").filter(~Q(ThirdPartyID = None), UserID__in=old_user_id)#.countaggregate(Sum("Payment"))
            old_user_count = len(old_user_id)
            summary_user_count += old_user_count
            old_user_trade_count = len(old_user_trades)
            summary_trade_count += old_user_trade_count
            old_total_fee = 0
            for old_user_trade in old_user_trades:
                old_total_fee += old_user_trade['Payment']
            summary_total_fee += old_total_fee
            old_avg_trade_fee = old_total_fee / old_user_trade_count
            old_total_fee = decimal.Decimal(old_total_fee).quantize(decimal.Decimal('0.00'))
            old_avg_trade_count = old_user_trade_count * 1.0 / old_user_count
            old_avg_trade_count = decimal.Decimal(old_avg_trade_count).quantize(decimal.Decimal('0.00'))
            old_avg_trade_fee = decimal.Decimal(old_avg_trade_fee).quantize(decimal.Decimal('0.00'))
            res.append({"Name":"老用户", "Count":old_user_count, "TotalFee": str(old_total_fee), "AvgTradeCount":str(old_avg_trade_count), "AvgTradeFee":str(old_avg_trade_fee)})
        else:
            res.append({"Name":"老用户", "Count":0, "TotalFee": 0, "AvgTradeCount":0, "AvgTradeFee":0})
        Log("SalesStatisticsData res: %s" % res, "local", "0.0.0.0", "DEBUG")
        
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
    
    
def TradesData(request):
    try:
        params = request.GET
        start=None
        end=None
        lesson_id=None
        offset=0
        limit=10
        sortOrder = '-'
        sortName = 'Name__count'
        
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        if params.has_key('sortOrder'):
            sortOrder = params['sortOrder']
            if sortOrder=='asc':
                sortOrder=''
            else:
                sortOrder='-'
        if params.has_key('sortName'):
            sortName = params['sortName']
            if sortName == 'TotalFee':
                sortName = 'Payment__sum'
            else:
                sortName = 'Name__count'
        
        sort = "%s%s" % (sortOrder,sortName)
        
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None),~Q(Payment = 0),IsRefund=0).order_by("PayTime")
        Log("TradesData params: %s" % params, "local", "0.0.0.0", "DEBUG")

        if params.has_key('category'):
            cate=params['category']
            if cate and cate != 'all':
                try:
                    cate=int(cate)
                    trades = trades.filter(LessonCategoryID=cate)
                except Exception,e:
                    cate = ''

        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                trades = trades.filter(ThirdPartyID__in=lesson_ids)
            except Exception,e:
                lesson_id = None
        if params.has_key('viewType') and params.get('viewType') != '':
            view_type = params['viewType']
            t = time.localtime(time.time())
            if view_type == 'daily':
                start =  datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d') 
                trades = trades.filter(PayTime__gt=start)
            elif view_type == 'weekly':
                start =  datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d 00:00:00'),'%Y-%m-%d %H:%M:%S') + datetime.timedelta(days = -(datetime.datetime.now().isoweekday()-1))
                trades = trades.filter(PayTime__gt=start)
            elif view_type == 'monthly':
                start =  datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-01 00:00:00'),'%Y-%m-%d %H:%M:%S')
                trades = trades.filter(PayTime__gt=start)
            end = datetime.datetime.now() + datetime.timedelta(days = 1)
        else:
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
        
        page = int(offset/limit + 1)
        
        group_trades = trades.values("Name").annotate(Count('Name'), Sum('Payment')).order_by(sort)
        
        #for trade in group_trades:
        #    res.append({"Name": trade['Name'], "Count": trade['Name__count'], "TotalFee": str(trade['Payment__sum'])})
        
        total = len(group_trades)
        res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        while i < last:
            trade = group_trades[i]
            res.append({"Name": trade['Name'], "Count": trade['Name__count'], "TotalFee": str(trade['Payment__sum'])})
            i=i+1

        obj = {
            "page":page,
            "rows":res,
            "total":total
        }


        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("TradesData error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps([]))
    
    
    

