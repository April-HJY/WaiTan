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

def CouponPage(request):
    template = loader.get_template('couponpage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))


def GetUserCoupons(mobile):
    #目前只有有赞
    try:
        token = GetYouzanToken()
        url="https://open.youzan.com/api/oauthentry/youzan.ump.promocard.buyer/3.0.1/search?access_token=%s&mobile=%s&status=%s" % (token,mobile,"VALID")
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        #Log("GetUserCoupons %s" %res, Type="DEBUG")
        #url="https://global.talk-cloud.net/WebAPI/entry/domain/%s/serial/%d/username/%s/usertype/2/ts/%s/auth/%d"
        
        return GetCouponsWithData(res['response'])
    except Exception,e:
        #Log("GetUserCoupons error: %s" %e, Type="DEBUG")
        return []
    
def GetUserInvalidCoupons(mobile):
    #目前只有有赞
    try:
        token = GetYouzanToken()
        url="https://open.youzan.com/api/oauthentry/youzan.ump.promocard.buyer/3.0.1/search?access_token=%s&mobile=%s&status=%s" % (token,mobile,"INVALID")
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        #Log("GetUserCoupons %s" %res, Type="DEBUG")
        #url="https://global.talk-cloud.net/WebAPI/entry/domain/%s/serial/%d/username/%s/usertype/2/ts/%s/auth/%d"
        invalid = GetCouponsWithData(res['response'])
        
        token = GetYouzanToken()
        url="https://open.youzan.com/api/oauthentry/youzan.ump.promocard.buyer/3.0.1/search?access_token=%s&mobile=%s&status=%s" % (token,mobile,"USED")
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        Log("GetUserCoupons %s" %res, Type="DEBUG")
        #url="https://global.talk-cloud.net/WebAPI/entry/domain/%s/serial/%d/username/%s/usertype/2/ts/%s/auth/%d"
        used = GetCouponsWithData(res['response'])
        
        return invalid + used
    except Exception,e:
        Log("GetUserCoupons error: %s" %e, Type="DEBUG")
        return []

def GetCouponsWithData(coupons):
        updateVar("Coupons")
        all_coupons = getVar("Coupons")
        user_coupons = []
        for c in coupons:
            for coupon in all_coupons:
                if int(c['coupon_group_id']) == coupon.CouponID:
                    c['Name'] = coupon.Name
                    c['fee'] = int(c['value'])/100.0
                    c['condition'] = coupon.Condition/100.0
                    c['start'] = GetDateStrByTimeStr(c['valid_start_at'])
                    c['end'] = GetDateStrByTimeStr(c['expire_at'])
                    if coupon.URL:
                        c['url'] = coupon.URL
                    else:
                        c['url'] = "https://h5.youzan.com/v2/showcase/homepage?alias=irvgfxqz&redirect_count=1"
                    #if coupon.DateType == 1:
                    #    c['start'] = coupon.ValidStartTime.strftime("%y/%m/%d")
                    #    c['end'] = coupon.ValidEndTime.strftime("%y/%m/%d")
                    #else:
                    #    start = time.strptime(c['take_at'], "%Y-%m-%d %H:%M:%S")
                    #    c['start'] = time.strftime("%y-%m-%d", start)
                    #    c['end'] = (start + datetime.timedelta(days = coupon.)).strftime("%y-%m-%d")
                    user_coupons.append(c)
                    #user_coupons.append(c)
                    #user_coupons.append(c)
        return user_coupons#res['response']
    
    
def UpdateYouzanCoupons(request):
    try:
        GetYouzanCouponsByPage()
        updateVar("Coupons")
        return HttpResponse("ok")
    except Exception,e:
        Log("talk_cloud_create_class error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
def GetAllCoupons(request):
    try:
        params = request.GET
        offset=0
        limit=10
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        page = int(offset/limit + 1)
        res = []
        all_coupons = getVar("Coupons")
        for coupon in all_coupons:
            if int(coupon.IsInvalid) == 0:
                edit = "<a href='javascript:popShow(%d)'>修改URL</a>" % (coupon.CouponID)
                res.append({"ID":coupon.CouponID, "Name":coupon.Name, "StartDate": coupon.ValidStartTime.strftime("%Y-%m-%d"), "EndDate": coupon.ValidEndTime.strftime("%Y-%m-%d"), 
                            "Coupon_URL":coupon.URL, "Edit": edit})
        total = len(res)
        x_res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        while i < last:
            x_res.append(res[i])
            i=i+1
            
        obj = {
            "page":page,
            "rows":x_res,
            "total":total,
        }
        #Log("GetAllCoupons obj %s" % obj, Type='DEBUG')
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("GetAllCoupons error: %s" % e, Type='DEBUG')
        return HttpResponse(e)

@csrf_exempt
def UpdateCouponUrl(request):
    try:
        params = request.POST
        coupon_id = params.get('coupon_id', None)
        coupon_url = params.get('coupon_url', None)
        coupon = Coupons.objects.filter(CouponID=coupon_id)
        if coupon:
            coupon[0].URL = coupon_url
            coupon[0].save()
            updateVar("Coupons")
        return HttpResponse('ok')
    except Exception,e:
        Log("UpdateCouponUrl error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
def GetYouzanCouponsByPage(page_no=1):
    youzan_token = GetYouzanToken()
    group_type = "PROMOCARD"
    page_size = 100
    url = """https://open.youzan.com/api/oauthentry/youzan.ump.coupon/3.0.0/search?access_token=%s&group_type=%s&page_no=%d&page_size=%d""" % (youzan_token,group_type,page_no, page_size)
    Log("GetYouzanCouponsByPage %s"% url, "local", "0.0.0.0", "DEBUG")
    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req)
    res = json.loads(res_data.read().decode('utf-8'))
    
    data = res['response']['groups']
    #Log("UpdateYouzanTrades length %d"% len(data), "local", "0.0.0.0", "DEBUG")
    for item in data:
        SaveYouzanCoupons(item)

    if res['response'].has_key('total') and res['response']['total'] > page_size * page_no:
        GetYouzanCouponsByPage(page_no+1)
    Log("GetYouzanCouponsByPage end %d" % len(data), "local", "0.0.0.0", "DEBUG")
    

def SaveYouzanCoupons(item):
    Log("SaveYouzanCoupons %s" % item, "local", "0.0.0.0", "DEBUG")
    coupon = Coupons.objects.filter(CouponID = item['id'])
    if coupon:
        coupon = coupon[0]
        
        coupon.Name=item['title']
        coupon.PreferentialType=item['preferential_type'] 
        coupon.Denominations=item['denominations']
        coupon.ValueRandomTo=item['value_random_to']
        coupon.Condition=item['condition']
        coupon.Discount=item['discount']
        coupon.IsLimit=item['is_limit']
        coupon.IsForbidPreference=item['is_forbid_preference']
        coupon.UserLevel=item['user_level']
        coupon.DateType=item['date_type']
        coupon.FixedTerm=item['fixed_term']
        coupon.FixedBeginTerm=item['fixed_begin_term']
        coupon.ValidStartTime=item['valid_start_time']
        coupon.ValidEndTime=item['valid_end_time']
        coupon.TotalQTY=item['total_qty']
        coupon.StockQTY=item['stock_qty']
        coupon.RangeType=item['range_type']
        coupon.RangeValue=item['range_value']
        coupon.ExpireNotice=item['expire_notice']
        coupon.Description=item['description']
        coupon.IsShare=item['is_share']
        coupon.IsInvalid=item['is_invalid']
        coupon.TotalTake=item['total_take']
        coupon.TotalUsed=item['total_used']
        coupon.Created=item['created_at']
        coupon.Updated=item['updated_at']
    else:
        coupon = Coupons(CouponID=item['id'], KDTID=item['kdt_id'], GroupType=item['group_type'], Name=item['title'], PreferentialType=item['preferential_type'], 
                    Denominations=item['denominations'], ValueRandomTo=item['value_random_to'], Condition=item['condition'], Discount=item['discount'],IsLimit=item['is_limit'],
                    IsForbidPreference=item['is_forbid_preference'], UserLevel=item['user_level'], DateType=item['date_type'], FixedTerm=item['fixed_term'],
                    FixedBeginTerm=item['fixed_begin_term'], ValidStartTime=item['valid_start_time'], ValidEndTime=item['valid_end_time'], TotalQTY=item['total_qty'],
                    StockQTY=item['stock_qty'], RangeType=item['range_type'], RangeValue=item['range_value'], ExpireNotice=item['expire_notice'],
                    Description=item['description'], IsShare=item['is_share'], IsInvalid=item['is_invalid'], TotalTake=item['total_take'], TotalUsed=item['total_used'],
                    Created=item['created_at'], Updated=item['updated_at'])
    coupon.save()
    
    
def GetAllUserCoupons(request):
    try:
        queue = TaskQueue('queue_name')
        i = 20000
        while i < 25000:
            task_url = "saveusercoupons/"
            paraDic = {
                "user_id":i
            }
            i += 1
            queue.add(Task(task_url, json.dumps(paraDic) ,delay=2))
        return HttpResponse("ok")
    except Exception,e:
        Log("GetAllUserCoupons error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    

@csrf_exempt
def SaveUserCoupons(request):
    try:
        #return HttpResponse('ok')
        params = json.loads(request.raw_post_data)
        #params = request.GET
        user_id = int(params.get('user_id',0))
        user = User.objects.get(ID=user_id)
        coupons = GetUserCoupons(user.Mobile)
        for coupon in coupons:
            c = UserCoupons.objects.filter(CouponID=coupon['id'])
            if not c:
                c = UserCoupons(UserID=user.ID, Mobile=user.Mobile, Name=user.Name, CouponName=coupon['Name'], Fee=float(coupon['fee']), ExpireAt=GetDateTimeByStr(coupon['expire_at']), 
                                TakeAt=GetDateTimeByStr(coupon['take_at']), IsValid=1, Created=datetime.datetime.now(), CouponID=int(coupon['id']), CouponGroupID=int(coupon['coupon_group_id']))
                c.save()
        return HttpResponse('ok')
    except Exception, e:
        Log("SaveUserCoupons error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
    
    
    