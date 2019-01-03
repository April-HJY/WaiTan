#coding: utf-8
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.http import *
from utils import *
from wxUtils import *
from django.views.decorators.csrf import csrf_exempt  
from itertools import *
from utils2 import *
from mem_db_sync import *
import urllib
import urllib2
import json
import httplib
import mimetypes
from tsaiPlatform import *



def MiniappTeacherPage(request):
    template = loader.get_template('miniappteacherpage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))


@csrf_exempt
def wxPrepayId(request):
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        prepay_id = GetwxPrepayId(params["appid"],params["price"],params["quantity"],params["attach"],params["body"],params["openid"],params["mchid"],params["notifyUrl"],params["name"],params["phone"],
                                  params["address"])
        Log("wxPrepayId %s"%prepay_id, "local", "0.0.0.0", "DEBUG")
        timeStamp = int(time.time())
        nonceStr='%d' %timeStamp
        values = {
              "appId":params["appid"],
              "timeStamp":timeStamp,
              "nonceStr":nonceStr,
              "package": "prepay_id=%s"%prepay_id,
              "signType": "MD5"
              } 
        sign=GetSign(values)
        resJSON = json.dumps({"package":"prepay_id=%s"%prepay_id,"timeStamp":timeStamp,"nonceStr":nonceStr,"sign":sign})
        
        return HttpResponse(resJSON)
    except Exception, e:
    #return HttpResponse('should use post method:%s'%params["appid"])
        Log("wxPrepayId error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)


def wechartWithdraw(request):
    appid = 'wx0c0e0edd8eaad932'
    mchid = '1415334402'
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        
        openid = params['openid']
        res = EnterprisePay(appid, params["amount"], openid, mchid, params["productCode"],params["productType"])

        return HttpResponse(res)
    except Exception, e:
        Log("wechatPrepayWithOpenId error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)
    
def wechatPrepay(request):
    appid = 'wxf11978168e04aba2'
    secret = 'e07e28bb5edad5140a9d8c2e1558e227'
    mchid = '1803200343373300'
    mchsecret = 'aacfdd841c8580afd0066d35fd75f816'
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        code = params['code']
        openid = GetOpenId(appid,secret,code)
        prepay_id = GetwxPrepayId(appid,params["price"],params["quantity"],params["productCode"],params["productType"],params["productName"],openid,mchid,params["notifyUrl"],params["name"],params["phone"],
                                  params["address"])
        Log("wechatPrepay %s"%prepay_id, "local", "0.0.0.0", "DEBUG")
        timeStamp = int(time.time())
        nonceStr='%d' %timeStamp
        values = {
            "appId":appid,
            "timeStamp":timeStamp,
            "nonceStr":nonceStr,
            "package": "prepay_id=%s"%prepay_id,
            "signType": "MD5"
        } 
        sign=GetSign(values)
        
        resJSON = json.dumps({"package":"prepay_id=%s"%prepay_id,"timeStamp":timeStamp,"nonceStr":nonceStr,"sign":sign})
        
        return HttpResponse(resJSON)
    except Exception, e:
        Log("wechatPrepay error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)

@csrf_exempt
def wechatOpenId(request):
    appid = 'wxf11978168e04aba2'
    secret = 'e07e28bb5edad5140a9d8c2e1558e227'
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        
        code = params['code']
        Log("wechatOpenId code%s"%code, "local", "0.0.0.0", "DEBUG")
        res = GetOpenId(appid,secret,code)
        
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("wechatOpenId error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)

    
def wechatPrepayWithOpenId(request):
    appid = 'wxf11978168e04aba2'
    secret = 'e07e28bb5edad5140a9d8c2e1558e227'
    mchid = '1803200343373300'
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        appid = params['appid']
        openid = params['openid']
        prepay_id = GetwxPrepayId(appid,params["price"],params["quantity"],params["productCode"],params["productType"],params["productName"],openid,mchid,params["notifyUrl"],params["name"],params["phone"],
                                  params["address"])
        Log("wechatPrepayWithOpenId %s"%prepay_id, "local", "0.0.0.0", "DEBUG")
        timeStamp = int(time.time())
        nonceStr='%d' %timeStamp
        values = {
            "appId":appid,
            "timeStamp":timeStamp,
            "nonceStr":nonceStr,
            "package": "prepay_id=%s"%prepay_id,
            "signType": "MD5"
        } 
        sign=GetSign(values)
        
        resJSON = json.dumps({"package":"prepay_id=%s"%prepay_id,"timeStamp":timeStamp,"nonceStr":nonceStr,"sign":sign})
        
        return HttpResponse(resJSON)
    except Exception, e:
        Log("wechatPrepayWithOpenId error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)
    
    
def WechatPrepayWithProductId(request):
    appid = 'wxf11978168e04aba2'
    secret = 'e07e28bb5edad5140a9d8c2e1558e227'
    mchid = '1499173302'
    mchsecret = 'IGWCHdS58OGbH4OkM1MIL9ZyV6QDQ1hp'
    notify_url = 'https://class.ddianke.com/PaidCallback'
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        Log("WechatPrepayWithProductId params:%s"%params, "local", "0.0.0.0", "DEBUG")
        openid = params.get('openid','')
        distributor_id = params.get("distributor_id",0)
        paidpoints = params.get("paidpoints",0)
        goods_json = json.loads(params.get('goodsJsonStr',''))
        #quantity = params.get('quantity',1)
        total_price = 0
        for goods in goods_json:
            quantity = int(goods.get('number',1))
            product_id = int(goods.get('goodsId', 0))
            product = MiniappProduct.objects.get(ID=goods['goodsId'])
            total_price += product.Price * quantity
            prepay_id = GetwxPrepayId(appid,product.Price,quantity,goods['goodsId'],product.Code,product.ProductTypeID,product.Name,openid,mchid,notify_url,goods_json,15,distributor_id,paidpoints)
            Log("WechatPrepayWithProductId %s"%prepay_id, "local", "0.0.0.0", "DEBUG")

        mobile = ''
        user_name = ''
        #目前只有一个商品，需要添加用户配置信息，以便将来选择
        if goods_json:
            msgs = goods_json[0].get('messages',[])
            for msg in msgs:
                content = msg.split(':')
                if len(content) == 2 and content[0] == '手机号码':
                    mobile = content[1]
        service_appid = 'wx457b9d0e6f93d1c5' #服务号
        wxuser = wxUser.objects.filter(openID = openid)
        isbound = False;
        if wxuser and wxuser[0].unionID:
            service_wxuser = wxUser.objects.filter(unionID = wxuser[0].unionID, SourceAccount = service_appid, Subscribed=1)
            if service_wxuser:
                isbound = True
                if not service_wxuser[0].MobileBound:
                    service_wxuser[0].MobileBound = 1
                    service_wxuser[0].save()
            else:
                service_wxuser = wxUser.objects.filter(Mobile=mobile, SourceAccount = service_appid, Subscribed=1)
                if service_wxuser:
                    isbound = True
                    if not service_wxuser[0].MobileBound:
                        service_wxuser[0].MobileBound = 1
                        service_wxuser[0].save()
        elif wxuser:
            service_wxuser = wxUser.objects.filter(Mobile=mobile, SourceAccount = service_appid, Subscribed=1)
            if service_wxuser:
                isbound = True
        res = {
            "code":0,
            "data":{"amountLogistics": 0, "score": 0, "goodsNumber": quantity, "isNeedLogistics": False, "amountTotle": total_price, "isbound":isbound},
            "msg":"success"
        }
        resJSON = json.dumps(res)
        #resJSON = json.dumps({"package":"prepay_id=%s"%prepay_id,"timeStamp":timeStamp,"nonceStr":nonceStr,"sign":sign})
        
        return HttpResponse(resJSON)
    except Exception, e:
        Log("WechatPrepayWithProductId error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)
    
    
def CreateOrder(request):
    appid = 'wxf11978168e04aba2'
    
    
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        Log("CreateOrder params:%s"%params, "local", "0.0.0.0", "DEBUG")
        openid = params.get('openid','')
        distributor_id = params.get("distributor_id",0)
        if not distributor_id:
            distributor_id = 0
        paidpoints = params.get("paidpoints",0)
        goods_json = json.loads(params.get('goodsJsonStr',''))
        #quantity = params.get('quantity',1)
        total_price = 0
        goods = goods_json[0]
        quantity = int(goods.get('number',1))
        product_id = int(goods.get('goodsId', 0))
        product = MiniappProduct.objects.get(ID=goods['goodsId'])
        total_price += product.Price * quantity

        channel_id = 15
        mobile = ''
        user_name = ''
        sku = []
        msgs = []
        wechat_code = ''
        age = 0
        grade = 0
        if goods_json:
            sku = goods_json[0].get('skus',[])
            msgs = goods_json[0].get('messages',[])
            for msg in msgs:
                content = msg.split(':')
                if len(content) == 2 and content[0] == '手机号码':
                    mobile = content[1]
                if len(content) == 2 and content[0] == '学生姓名':
                    user_name = content[1]
                if len(content) == 2 and content[0] == '微信号':
                    wechat_code = content[1]
                if len(content) == 2 and content[0] == '学生年龄':
                    try:
                        age = int(content[1])
                    except:
                        age = 0
                if len(content) == 2 and content[0].startswith('学生年级'):
                    try:
                        grade = int(content[1])
                    except:
                        grade = 0
        wxuser = None
        if mobile:
            wxuser = wxUserClass(appid,openid)
            wxuser.wxUserData.Mobile = mobile
            wxuser.wxUserData.save()
            user = User.objects.filter(Mobile=mobile)
            nickname = username = ''
            if wxuser.wxUserData.Name:
                nickname = username = wxuser.wxUserData.Name
            if user_name:
                username = user_name
            if not user:
                area = GetUserAreaByMobile(mobile)
                province = ''
                city = ''
                user_zip = ''
                segmentName = ''
                if type(area) is dict:
                    province = area.get('province', '')
                    city = area.get('cityName', '')
                    user_zip = area.get('postCode', '')
                    segmentName = area.get('segmentName', '')
                user = User(IsImported=False, Name=nickname, NickName=nickname, Mobile=mobile, ChannelID=channel_id, DistributorName=None, Province=province, 
                           City=city, Zip=user_zip, SegmentName=segmentName, ChildAge = age, ChildGrade = grade, ChildName=username)
                user.save()
            else:
                user = user[0]
                if username:
                    user.ChildName = username
                if nickname:
                    user.NickName = nickname
                if age:
                    user.ChildAge=age
                if grade:
                    user.ChildGrade=grade
                user.save()

        nonce_str = int(time.time()*1000)
        c = OITM(ProductID=product_id,ProductCode = product.Code,ProductType = product.ProductTypeID,ProductName = product.Name ,AppID=appid, PaidOpenId= openid , Quantity = quantity, TotalAmount = total_price, 
                 TradeNumber = nonce_str, wxPayURL =  '', PrePay_ID = '', SKU=';'.join(sku), Messages=json.dumps(msgs), Mobile=mobile,ChannelID=channel_id,
                 DistributorID=distributor_id, PaidPoints=paidpoints)#小程序的ChannelID
        c.save()
        
        service_appid = 'wx457b9d0e6f93d1c5' #服务号
        isbound = False;
        if wxuser and wxuser.wxUserData.unionID:
            service_wxuser = wxUser.objects.filter(unionID = wxuser.wxUserData.unionID, SourceAccount = service_appid, Subscribed=1)
            if service_wxuser:
                isbound = True
                if not service_wxuser[0].MobileBound:
                    service_wxuser[0].MobileBound = 1
                    service_wxuser[0].save()
            else:
                service_wxuser = wxUser.objects.filter(Mobile=mobile, SourceAccount = service_appid, Subscribed=1)
                if service_wxuser:
                    isbound = True
                    if not service_wxuser[0].MobileBound:
                        service_wxuser[0].MobileBound = 1
                        service_wxuser[0].save()
        elif wxuser:
            service_wxuser = wxUser.objects.filter(Mobile=mobile, SourceAccount = service_appid, Subscribed=1)
            if service_wxuser:
                isbound = True
                
        res = {
            "code":0,
            "data":{"amountLogistics": 0, "score": 0, "goodsNumber": quantity, "isNeedLogistics": False, "amountTotle": total_price, "isbound":isbound, "order_id":c.ID},
            "msg":"success"
        }
        resJSON = json.dumps(res)
        #resJSON = json.dumps({"package":"prepay_id=%s"%prepay_id,"timeStamp":timeStamp,"nonceStr":nonceStr,"sign":sign})
        
        return HttpResponse(resJSON)
    except Exception, e:
        Log("CreateOrder error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)
    
    
def GetOrderInfo(request):
    try:        
        params = request.GET
        Log("GetOrderInfo params: %s" % params, Type="DEBUG")
        order_id = params.get('order_id', 0)
        oitm = OITM.objects.get(ID=order_id)
        product = MiniappProduct.objects.get(ID=oitm.ProductID)
        wxuser = wxUser.objects.get(openID = oitm.PaidOpenId)
        point_limit = 0
        Log("GetOrderInfo s: %s" % GetUserPointRate('paidRate'), Type="DEBUG")
        if product.PointLimit:
            point_limit = product.PointLimit
        else:
            point_limit = round(oitm.TotalAmount * GetUserPointRate('paidRate').Rate / 100)
            if point_limit == 0 and oitm.TotalAmount > 100:
                point_limit = 1
        if point_limit > wxuser.Points:
            point_limit = wxuser.Points
        status = ''
        if oitm.Paid == 0:
            status = "待付款"
        elif oitm.Paid == 1:
            status = "已付款"
        elif oitm.Paid == 3:
            status = "已退款"
        res = {
            "code":0,
            "data":{"curr_price": oitm.TotalAmount, "display_price": oitm.TotalAmount/100.0, "openid": wxuser.openID, "user_points": wxuser.Points, "point_limit": point_limit, 
                    "quantity": oitm.Quantity, "name":oitm.ProductName, "order_id":oitm.ID, "title_img":product.ProductUrl1,"date_at":oitm.TradeTime.strftime("%Y-%m-%d %H:%M:%S"),
                   "trade_no":oitm.TradeNumber,"statusStr":status,"sku":oitm.SKU},
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetOrderInfo error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
def PayOrder(request):
    mchid = '1499173302'
    notify_url = 'https://class.ddianke.com/PaidCallback'
    try:        
        params = request.GET
        Log("PayOrder params: %s" % params, Type="DEBUG")
        order_id = params.get('order_id', 0)
        use_points = params.get('use_points', 0)
        if use_points:
            use_points = int(use_points)
        curr_amount = params.get('curr_amount', 0)
        if curr_amount:
            curr_amount = int(curr_amount)
        oitm = OITM.objects.get(ID=order_id)
        product = MiniappProduct.objects.get(ID=oitm.ProductID)
        wxuser = wxUser.objects.get(openID = oitm.PaidOpenId)
        point_limit = 0
        if product.PointLimit:
            point_limit = product.PointLimit
        else:
            point_limit = round(oitm.TotalAmount * GetUserPointRate('paidRate').Rate / 100)
            if point_limit == 0 and oitm.TotalAmount > 100:
                point_limit = 1
        if point_limit > wxuser.Points:
            point_limit = wxuser.Points
        Log("PayOrder use_points,point_limit: %d %d" % (use_points,point_limit), Type="DEBUG")
        if use_points > point_limit:
            res = {
                "code":1,
            	"msg":"积分使用超过上限"
            }
        elif curr_amount < (oitm.TotalAmount-use_points*100):
            res = {
                "code":2,
            	"msg":"价格有误"
            }
        else:
            (prepay_id,out_trade_no) = GetPrepayId(oitm.AppID,curr_amount,oitm.Quantity,oitm.ProductCode,oitm.ProductName,oitm.PaidOpenId,mchid,notify_url)
            if not prepay_id or not out_trade_no:
                res = {
                    "code":3,
                    "msg":"创建订单错误"
                }
            else:
                timeStamp = int(time.time())
                nonceStr='%d' %timeStamp
                values = {
                    "appId":oitm.AppID,
                    "timeStamp":timeStamp,
                    "nonceStr":nonceStr,
                    "package": "prepay_id=%s"%prepay_id,
                    "signType": "MD5"
                }
                sign=GetSign(values)
                unit_price = oitm.TotalAmount/oitm.Quantity
                oitm.PaidPoints = use_points
                oitm.TotalAmount = curr_amount
                oitm.PrePay_ID = prepay_id
                oitm.TradeNumber = out_trade_no
                oitm.save()
                res = {
                    "code":0,
                    "data":{"package":"prepay_id=%s"%prepay_id,"timeStamp":str(timeStamp),"nonceStr":str(nonceStr),"sign":sign,"goodsName":product.Name,"pic":product.ProductUrl1,
                        "amount":oitm.TotalAmount,"display_amount":str(GetDecimal(oitm.TotalAmount/100.0)),"prepay_id":prepay_id,"id":oitm.ID,"paid":oitm.Paid, "quantity":oitm.Quantity},
                    "msg":"success"
                }

        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("PayOrder error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
def OrderRefund(request):
    try:        
        params = request.POST
        Log("mini_OrderRefund params: %s" % params, Type="DEBUG")
        order_id = params.get('trade_id', 0)
        res = OrderRefund(order_id)
        return HttpResponse(res)
    except Exception,e:
        Log("mini_OrderRefund error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    

def CancelOrder(request):
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        Log("CancelOrder params:%s"%params, "local", "0.0.0.0", "DEBUG")
        appid = params['appid']
        openid = params['openid']
        order_id = int(params['order_id'])
        order = OITM.objects.get(PaidOpenId=openid,Paid=0,ID=order_id)
        order.Paid=-1
        order.save()
        return HttpResponse('ok')
    except Exception, e:
        Log("CancelOrder error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

    
def GetOrderList(request):
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        Log("GetOrderList params:%s"%params, "local", "0.0.0.0", "DEBUG")
        appid = params['appid']
        openid = params['openid']
        status = int(params['status'])
        orders = []
        
        if status == 0:
            orders = OITM.objects.filter(PaidOpenId=openid,Paid=0,TradeTime__gt=(datetime.now() - timedelta(minutes = 30)))
        elif status == 1:
            orders = OITM.objects.filter(PaidOpenId=openid).filter(Q(Paid=2) | Q(Paid=3))
        elif status == 2:
            orders = OITM.objects.filter(PaidOpenId=openid,Paid=1)
        
        res = []
        for order in orders:
            date_at = order.TradeTime.strftime("%Y-%m-%d %H:%M:%S")
            product = MiniappProduct.objects.get(ID=order.ProductID)
            timeStamp = int(time.time())
            nonceStr='%d' %timeStamp
            prepay_id = order.PrePay_ID
            values = {
                "appId":appid,
                "timeStamp":timeStamp,
                "nonceStr":nonceStr,
                "package": "prepay_id=%s"%prepay_id,
                "signType": "MD5"
            }
            sign=GetSign(values)
            statusStr = ''
            if order.Paid == 0:
                statusStr = '待付款'
            if order.Paid == 1:
                statusStr = '已完成'
            elif order.Paid == 2:
                statusStr = '退款中'
            elif order.Paid == 3:
                statusStr = '已退款'
            unit_price = order.TotalAmount/order.Quantity
            res.append({"package":"prepay_id=%s"%prepay_id,"timeStamp":str(timeStamp),"nonceStr":str(nonceStr),"sign":sign,"dateAdd":date_at,"goodsName":product.Name,"pic":product.ProductUrl1,
                        "amount":order.TotalAmount,"display_amount":str(GetDecimal(order.TotalAmount/100.0)),"prepay_id":prepay_id,"id":order.ID,"paid":order.Paid, "statusStr":statusStr,
                       "unit_price":str(GetDecimal(unit_price/100.0)), "quantity":order.Quantity,"PaidPoints":order.PaidPoints})
        resJSON = {
            "code":0,
            "data":res,
            "msg":"success"
        }
        #Log("GetOrderList res:%s"%res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(resJSON))
    except Exception, e:
        Log("GetOrderList error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    

def UpdateUserInfo(request):
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        appid = params['appid']
        openid = params['openid']
        userInfo = params['userInfo']
        #Log("UpdateUserInfo user:%s"%userInfo, "local", "0.0.0.0", "DEBUG")
        user = wxUserClass(appid,openid)
        
        user.SetUserInfo(json.loads(userInfo))
        
        updateVar('miniappUser')
        
        return HttpResponse('success')
    except Exception, e:
        Log("UpdateUserInfo error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)


def GetUserInfo(request):
    try:
        params = request.GET
        if False:#params.has_key('openid') and params.has_key('appid'):
            users = getVar('miniappUser').filter(openID = params['openid'])
            #users = wxUser.objects.all().filter(openID = params['openid'], SourceAccount = params['appid'])
            if len(users) > 0:
                user = users[0]
                topicCount = len(getVar('Topic').filter(openID = user.openID))
                commentCount = len(getVar('Comment').filter(openID = user.openID))
                birthday = ''
                if user.Birthday != None:
                    birthday = user.Birthday.strftime("%Y-%m-%d")
                workDate = ''
                if user.DateOfFirstJob != None:
                    workDate = user.DateOfFirstJob.strftime("%Y-%m-%d")
                res = {'openid':user.openID, 'birthday':birthday, 'company':user.Company, 'industry':user.Industry, 'salary':user.Salary, 'province': user.Province2, 'city':user.City2, 
                       'workDate': workDate, 'university': user.University, 'major':user.Major, 'growth':user.Growth, 'topicCount':topicCount, 'commentCount':commentCount}
                resJSON = json.dumps(res)
                return HttpResponse(resJSON)
        return HttpResponse('no user')
    except Exception, e:
        Log("GetUserInfo Error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)


def UpdateFormid(request):
    params = request.GET
    res = 'success'
    if params.has_key('openid') and params.has_key('formid'):
        openid = params['openid']
        formid = params['formid']
        nick = params['nickname']
        res = SaveFormid(openid, formid, nick)
    else:
        res = 'params missed'
    return HttpResponse(res)


def TestTemplateMsg(request):
    params = request.GET
    openid = params['openid']
    res = SendTemplateMsg(openid, '')
    template = loader.get_template('templatetest.html')

    context = RequestContext(request, res)
    return HttpResponse(template.render(context))

def TestFunction(request):
    try:
        url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=%s' %  GetMiniappAccessToken()
        data = {'page':"pages/campaign/index", 'scene':'12345'}
        with requests.Session() as s:
            r = s.post(url,json.dumps(data),stream=True)
        temp_storage = io.BytesIO()
        #for block in r.iter_content(1024):
        temp_storage.write(r.content)
        buffer = StringIO.StringIO(temp_storage.getvalue())
        base64_str = 'data:image/png;base64,%s' % base64.b64encode(buffer.getvalue())
        return HttpResponse(base64_str)
    except Exception, e:
        Log("TestFunction error: %s" % e,"local", "0.0.0.0", "DEBUG")
        return HttpResponse('error')


def GetAudio(request):
    audio =  {
        #降低请求数，分享的文字和图片url先放这里
        'shareText': '',
        'shareImg': '',
        'avatar': 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKVZ6DCRjGtoG5fVNLZtozSAaDvCcpkrJJQdH8vMegaLQYcE066hWXcPjpmhkCULvUx7d7xEx8A9Q/0',
        'poster': 'http://y.gtimg.cn/music/photo_new/T002R300x300M000003rsKF44GyaSk.jpg?max_age=2592000',
    'name': '心智模型决定了转型成败',
    'author': '生菜',
    'src': 'https://tsaistorage-1254256984.cos.ap-beijing.myqcloud.com/audio/0518.m4a',
    'src2': 'http://ws.stream.qqmusic.qq.com/M500001VfvsJ21xFqb.mp3?guid=ffffffff82def4af4b12b3cd9337d5e7&uin=346897220&vkey=6292F51E1E384E061FF02C31F716658E5C81F5594D561F2E88B854E81CAAB7806D5E4F103E55D33C16F3FAC506D1AB172DE8600B37E43FAD&fromtag=88',
  }
    res = json.dumps(audio)
    return HttpResponse(res)

    
def GetMiniappProducts(request):
    try:
        params = request.GET
        Log("GetMiniappProducts params: %s" % params, "local", "0.0.0.0", "DEBUG")
        prod_list = []
        condition = params.get('nameLike')
        products = []
        if condition:
            products = MiniappProduct.objects.filter(Name__contains=condition)
        else:
            products = getVar("MiniappProduct")
        #if condition:
        #    products = products.filter(ProductName__contains=condition)
        for product in products:
            #edit = "<a href='javascript:putaway_product(%d)'>上架</a>&nbsp;<a href='javascript:edit_product(%d)'>修改</a>&nbsp;<a href='javascript:delete_product(%d)'>删除</a>" % (product.ID,product.ID,product.ID)
            prod_list.append({"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUName": product.SKUName, "Price": str(GetDecimal(product.Price/100.0)), 
                              "ProductUrl1": product.ProductUrl1, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                              "ProductUrl5": product.ProductUrl5, "Inventory": product.Inventory, "OriginalPrice":str(GetDecimal(product.OriginalPrice/100.0)),"CostPrice":str(GetDecimal(product.CostPrice/100.0)),
                              "Messages":product.Messages})
        res = {
            "code":0,
            "data":prod_list,
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetMiniappProducts error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetMiniappProductsByCategory(request):
    try:
        
        params = request.GET
        Log("GetMiniappProductsByCategory params: %s" % params, "local", "0.0.0.0", "DEBUG")
        cate_id = params.get("category_id",0)
        openid = params.get("openid",'')
        category_list = []
        #category_id_list = []
        condition = params.get('nameLike')
        categories = []
        if cate_id:
            categories = getVar('LessonCategory').filter(ID=cate_id)
        else:
            categories = getVar('LessonCategory')
        relation = getVar('ProductAndProductTag')
        tags = getVar('ProductTag')
        products = []
        if condition:
            products = MiniappProduct.objects.filter(Name__contains=condition, IsDisplay=1).order_by("Order","-ID")
        else:
            products = MiniappProduct.objects.filter(IsDisplay=1).order_by("Order","-ID")
        #if condition:
        #    products = products.filter(ProductName__contai=condition)
        
        for category in categories:
            
            tag_list = []
            if category.ShowTag:
                for tag in tags:
                    show_count = tag.ShowCount
                    prod_list = []
                    product_id_list = []
                    for r in relation:
                        if tag.ID == r.ProductTagID:
                            product_id_list.append(r.ProductID)
                    
                    for product in products:
                        if product.LessonCategoryID == category.ID and product.ProductID in product_id_list:
                            if show_count <= 0 and cate_id == 0:
                                break;
                            show_count -= 1
                            properties = product.ProductProperties.split(';')
                            prod_list.append({"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUName": product.SKUName, "Price": str(GetDecimal(product.Price/100.0)), 
                                      "ProductUrl1": product.ProductUrl1, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                                      "ProductUrl5": product.ProductUrl5, "Inventory": product.Inventory, "OriginalPrice":str(GetDecimal(product.OriginalPrice/100.0)),
                                      "CostPrice":str(GetDecimal(product.CostPrice/100.0)),"Messages":product.Messages,"ProductProperties":properties,"TeacherDesc":product.TeacherDesc})
                    if prod_list:
                        tag_list.append({"ID":tag.ID,"Code":tag.Code,"TitleImg":tag.TitleImg,"Name":tag.Name,"FullName":tag.FullName,"Products":prod_list})
                if tag_list:
                    category_list.append({"ID":category.ID,"iconUrl":category.Icon,"TitleImg":category.TitleImg,"Name":category.Name,"FullName":category.FullName,"Tags":tag_list, "ShowTag":True, "ShowProduct":False})
            else:
                prod_list = []
                show_count = category.ShowCount
                for product in products:
                        if product.LessonCategoryID == category.ID:
                            if show_count <= 0 and cate_id == 0:
                                break;
                            show_count -= 1
                            #Log("GetMiniappProductsByCategory prod_id %d" % product.ProductID, "local", "0.0.0.0", "DEBUG")
                            #edit = "<a href='javascript:putaway_product(%d)'>上架</a>&nbsp;<a href='javascript:edit_product(%d)'>修改</a>&nbsp;<a href='javascript:delete_product(%d)'>删除</a>" % (product.ID,product.ID,product.ID)
                            properties = product.ProductProperties.split(';')
                            prod_list.append({"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUName": product.SKUName, "Price": str(GetDecimal(product.Price/100.0)), 
                                      "ProductUrl1": product.ProductUrl1, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                                      "ProductUrl5": product.ProductUrl5, "Inventory": product.Inventory, "OriginalPrice":str(GetDecimal(product.OriginalPrice/100.0)),
                                      "CostPrice":str(GetDecimal(product.CostPrice/100.0)),"Messages":product.Messages,"ProductProperties":properties,"TeacherDesc":product.TeacherDesc})
                if prod_list:
                    category_list.append({"ID":category.ID,"iconUrl":category.Icon,"TitleImg":category.TitleImg,"Name":category.Name,"FullName":category.FullName,"Products":prod_list, "ShowTag":False, "ShowProduct":True})
        res = {
            "code":0,
            "data":category_list,
            "msg":"success"
        }
        #Log("GetMiniappProductsByCategory res: %s" % res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetMiniappProductsByCategory error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetHeatMiniappProducts(request):
    try:
        params = request.GET
        Log("GetHeatMiniappProducts params: %s" % params, "local", "0.0.0.0", "DEBUG")
        test_list = ['oFrat4os3IPoFKUuRmAdHIN48M3c','oFrat4mK9GNzRbK037gtGLEiKZ9c']
        category_list = []
        #category_id_list = []
        condition = params.get('nameLike')
        openid = params.get("openid",'')
        relation = ProductAndProductTag.objects.values("ProductID").filter(ProductTagID=1)
        Log("GetHeatMiniappProducts relation: %s" % relation, "local", "0.0.0.0", "DEBUG")
        product_ids = []
        for r in relation:
            product_ids.append(r['ProductID'])
        #tag = getVar('ProductTag').get(ID=1)
        products = []
        if condition:
            products = MiniappProduct.objects.filter(Name__contains=condition, IsDisplay=1).order_by("Order","-ID")
        else:
            products = MiniappProduct.objects.filter(IsDisplay=1).order_by("Order","-ID")

        prod_list = []
        if openid in test_list:
            product = MiniappProduct.objects.filter(ID=31)
            if product:
                product = product[0]
                prod_list.append({"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUName": product.SKUName, "Price": str(GetDecimal(product.Price/100.0)), 
                                      "ProductUrl1": product.ProductUrl1, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                                      "ProductUrl5": product.ProductUrl5, "Inventory": product.Inventory, "OriginalPrice":str(GetDecimal(product.OriginalPrice/100.0)),
                                      "CostPrice":str(GetDecimal(product.CostPrice/100.0)),"Messages":product.Messages})
        for product in products:
                    if product.ProductID in product_ids:
                        #Log("GetMiniappProductsByCategory prod_id %d" % product.ProductID, "local", "0.0.0.0", "DEBUG")
                        #edit = "<a href='javascript:putaway_product(%d)'>上架</a>&nbsp;<a href='javascript:edit_product(%d)'>修改</a>&nbsp;<a href='javascript:delete_product(%d)'>删除</a>" % (product.ID,product.ID,product.ID)
                        prod_list.append({"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUName": product.SKUName, "Price": str(GetDecimal(product.Price/100.0)), 
                                      "ProductUrl1": product.ProductUrl1, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                                      "ProductUrl5": product.ProductUrl5, "Inventory": product.Inventory, "OriginalPrice":str(GetDecimal(product.OriginalPrice/100.0)),
                                      "CostPrice":str(GetDecimal(product.CostPrice/100.0)),"Messages":product.Messages})

        res = {
            "code":0,
            "data":prod_list,
            "msg":"success"
        }
        #Log("GetHeatMiniappProducts res: %s" % res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetHeatMiniappProducts error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetMiniappProductDetail(request):
    try:
        params = request.GET
        Log("GetMiniappProductDetail params: %s" % params, "local", "0.0.0.0", "DEBUG")
        product_id = params.get('id')
        product = MiniappProduct.objects.get(ID=product_id)
        videos = ['mp4','avi','wmv']
        rl_isvideo2 = is_vedio(product.ProductUrl2)
        rl_isvideo3 = is_vedio(product.ProductUrl3)
        rl_isvideo4 = is_vedio(product.ProductUrl4)
        rl_isvideo5 = is_vedio(product.ProductUrl5)
        rl_isvideo6 = is_vedio(product.ProductUrl6)
        rl_isvideo7 = is_vedio(product.ProductUrl7)
        rl_isvideo8 = is_vedio(product.ProductUrl8)
        rl_isvideo9 = is_vedio(product.ProductUrl9)
        rl_isvideo10 = is_vedio(product.ProductUrl10)
        rl_isvideo11 = is_vedio(product.ProductUrl11)
        
        messages = ProductMessage.objects.filter(ProductID = product.ID)
        msg_type_dic = GetMessageTypeDic();
        msg=[]
        for message in messages:
            msg_type = msg_type_dic[message.ProductMessageTypeID]
            msg.append({"message_id":message.ID,"message_name":message.Name.strip(), "message_type_id": message.ProductMessageTypeID, "InputType":msg_type.InputType, "Placeholder":msg_type.Placeholder,
                       "RegularExpression":msg_type.RegularExpression})
        skus = []
        Log("GetMiniappProductDetail sku: %s" % product.SKUName, "local", "0.0.0.0", "DEBUG")
        if product.SKUName.strip():
            skus = json.loads(product.SKUName)

        prod = {"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUs": skus, "Price": str(GetDecimal(product.Price/100.0)), 
                "ProductUrl1": product.ProductUrl1, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,"ProductUrl5": product.ProductUrl5, 
                "ProductUrl6": product.ProductUrl6, "ProductUrl7": product.ProductUrl7, "ProductUrl8": product.ProductUrl8, "ProductUrl9": product.ProductUrl9,"ProductUrl10": product.ProductUrl10,
                "ProductUrl11": product.ProductUrl11, "Inventory": product.Inventory, "OriginalPrice":str(GetDecimal(product.OriginalPrice/100.0)), "CostPrice":str(GetDecimal(product.CostPrice/100.0)),"Messages":msg,
                "rl_isvideo2":rl_isvideo2,"rl_isvideo3":rl_isvideo3,"rl_isvideo4":rl_isvideo4,"rl_isvideo5":rl_isvideo5, "rl_isvideo6":rl_isvideo6,"rl_isvideo7":rl_isvideo7,"rl_isvideo8":rl_isvideo8,
                "rl_isvideo9":rl_isvideo9, "rl_isvideo10":rl_isvideo10, "rl_isvideo11":rl_isvideo11, "DistributePoint":product.DistributePoint, "DistributeCashback":product.DistributeCashback, 
                "PointLimit":product.PointLimit}
        Log("GetMiniappProductDetail prod:%s"%prod, "local", "0.0.0.0", "DEBUG")
        res = {
            "code":0,
            "data":{"basicInfo":prod},
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetMiniappProductDetail error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetMessageTypeDic():
    message_types = getVar("ProductMessageType")
    dic = {}
    for message_type in message_types:
        dic[message_type.ID] = message_type
    return dic


def is_vedio(url_str):
    if url_str:
        videos = ['mp4','avi','wmv']
        strs = url_str.split('.')
        end_str = strs[len(strs)-1]
        return (end_str.lower() in videos)
    else:
        return False
        
        
def GetMiniappTeachers(request):
    try:
        Log("GetMiniappTeachers ", "local", "0.0.0.0", "DEBUG")
        teacher_list = []
        teachers = getVar("MiniappTeacher")
        #if condition:
        #    products = products.filter(ProductName__contains=condition)
        for teacher in teachers:
            edit = "<a href='javascript:edit_teacher(%d)'>修改</a>&nbsp;<a href='javascript:delete_teacher(%d)'>删除</a>" % (teacher.ID,teacher.ID)
            teacher_list.append({"ID":teacher.ID,"Name":teacher.Name, "TeacherUrl1": teacher.TeacherUrl1, "TeacherUrl2": teacher.TeacherUrl2, "TeacherUrl3": teacher.TeacherUrl3, "TeacherUrl4": teacher.TeacherUrl4,
                        "TeacherUrl5": teacher.TeacherUrl5,"Edit":edit})
        Log("GetMiniappTeachers res:%s" % teacher_list, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(teacher_list))
    except Exception, e:
        Log("GetMiniappTeachers error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetTeachers(request):
    try:
        Log("GetTeachers ", "local", "0.0.0.0", "DEBUG")
        teacher_list = []
        teachers = getVar("MiniappTeacher")
        #if condition:
        #    products = products.filter(ProductName__contains=condition)
        for teacher in teachers:
            edit = "<a href='javascript:edit_teacher(%d)'>修改</a>&nbsp;<a href='javascript:delete_teacher(%d)'>删除</a>" % (teacher.ID,teacher.ID)
            teacher_list.append({"ID":teacher.ID,"Name":teacher.Name, "TeacherUrl1": teacher.TeacherUrl1, "TeacherUrl2": teacher.TeacherUrl2, "TeacherUrl3": teacher.TeacherUrl3, "TeacherUrl4": teacher.TeacherUrl4,
                        "TeacherUrl5": teacher.TeacherUrl5,"Edit":edit})
        Log("GetTeachers res:%s" % teacher_list, "local", "0.0.0.0", "DEBUG")
        res = {
            "code":0,
            "data":teacher_list,
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetTeachers error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
        
        
@csrf_exempt
def SaveMiniappTeacher(request):
    try:
        params = request.POST
        Log("SaveMiniappTeacher params: %s" % params, "local", "0.0.0.0", "DEBUG")
        update_id = params.get('id', None)
        teacher_name = params.get('teacher_name')
        teacher_url1 = params.get('teacher_url1', '')
        teacher_url2 = params.get('teacher_url2', '')
        teacher_url3 = params.get('teacher_url3', '')
        teacher_url4 = params.get('teacher_url4', '')
        teacher_url5 = params.get('teacher_url5', '')
        if update_id:
            teacher = MiniappTeacher.objects.get(ID=update_id)
            teacher.Name = teacher_name
            teacher.TeacherUrl1 = teacher_url1
            teacher.TeacherUrl2 = teacher_url2
            teacher.TeacherUrl3 = teacher_url3
            teacher.TeacherUrl4 = teacher_url4
            teacher.TeacherUrl5 = teacher_url5
            teacher.save()
        else:
            teacher = MiniappTeacher(Name=teacher_name, TeacherUrl1=teacher_url1, TeacherUrl2=teacher_url2, TeacherUrl3=teacher_url3, 
                              TeacherUrl4=teacher_url4, TeacherUrl5=teacher_url5)
            teacher.save()
        updateVar("MiniappTeacher")
        return HttpResponse('ok')
    except Exception,e:
        Log("SaveMiniappTeacher error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def DeleteMiniappTeacher(request):
    try:
        params = request.POST
        Log("DeleteMiniappTeacher params: %s" % params, "local", "0.0.0.0", "DEBUG")
        delete_id = params.get('id', None)
        
        if delete_id:
            teacher = MiniappTeacher.objects.get(ID=delete_id)
            teacher.delete()
        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteMiniappTeacher error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetBannerList(request):
    try:
        params = request.GET
        Log("GetBannerList params: %s" % params, "local", "0.0.0.0", "DEBUG")
        category_id = params.get('category_id',0)
        banners = []
        if category_id:
            banners = getVar("MiniappBanner").filter(LessonCategoryID = category_id).order_by("Order","ID")
        else:
            banners = getVar("MiniappBanner").filter(ShowOnMainpage=1).order_by("Order","ID")
        banner_list = []
        for banner in banners:
            banner_list.append({"ID":banner.ID,"linkUrl":"","order":banner.Order,"picUrl":banner.URL,"remark":"","title":"课程","linkid":banner.LinkProductID})

        res = {
            "code":0,
            "data":banner_list,
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetBannerList error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetCategories(request):
    try:
        params = request.GET
        Log("GetCategories params: %s" % params, "local", "0.0.0.0", "DEBUG")
        categories = getVar("LessonCategory")
        cates = []
        for cate in categories:
            if cate.FullName:
                cates.append({"ID":cate.ID,"iconUrl":cate.Icon,"Name":cate.Name,"FullName":cate.FullName})
        #banners = [{"ID":1,"linkUrl":"","order":0,"picUrl":"https://tsaistorage-1254256984.cos.ap-beijing.myqcloud.com/img/waitan/banner/9.png","remark":"","title":"课程","module":"main"}]
        res = {
            "code":0,
            "data":cates,
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetCategories error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    


@csrf_exempt
def CustomMessage(request):
    try:
        params = json.loads(request.raw_post_data)
        Log("CustomMessage params: %s" % params, "local", "0.0.0.0", "DEBUG")
        openid = params.get("FromUserName",'')
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % GetMiniappAccessToken()
        msg = {
            "touser": str(openid),
            "msgtype": "link",
            "link": {
                "title": "外滩云课堂",
                "description": "关注外滩云课堂，获得更优质的服务",
                "url": "http://applinzi.ddianke.com/wxJSWeb/subscribe_service?mini_openid=%s"%str(openid),
                "thumb_url": "https://tsaistorage-1254256984.cos.ap-beijing.myqcloud.com/img/waitan/logo_square.png"
            }
        }
        Log("CustomMessage msg: %s" % msg, "local", "0.0.0.0", "DEBUG")
        res = Post(url,msg)
        Log("CustomMessage res: %s" % res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')
    except Exception, e:
        Log("CustomMessage error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetMiniappUserInfo(request):
    try:
        params = request.GET
        appid = "wxf11978168e04aba2"
        secret = "e07e28bb5edad5140a9d8c2e1558e227"
        token = params.get('login_code','')
        user_info = params.get('user_info','')
        Log("GetMiniappUserInfo params: %s" % params, "local", "0.0.0.0", "DEBUG")
        url = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code"  % (appid,secret,token)
        response = urllib2.urlopen(url) 
        res = response.read().decode("utf8")
        res_obj = json.loads(res)
        openid = res_obj.get("openid")
        unionid = res_obj.get("unionid",'')
        if user_info:
            user_info = json.loads(user_info);
            user_info['unionid'] = unionid
        else:
            user_info = {}
            user_info['unionid'] = unionid
        user = wxUserClass(appid,openid)
        if user_info:
            user.SetUserInfo(user_info)
        user_id = user.wxUserData.ID
        is_new = False
        if user_id:
            new_points = UserPointDetail.objects.filter(wxUserID=user_id, Reason='新用户')
            if not new_points:
                is_new = True
                point_views.UpdatePointToUser(user_id, 99, object_type='wxUser', object_id=user_id, reason='新用户')
        Log("GetMiniappUserInfo openid: %s" % openid, "local", "0.0.0.0", "DEBUG")
        res = {
            "code":0,
            "data":{
                "openid":openid,
                "isNew":is_new
            },
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetMiniappUserInfo error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetBindingQRCode(request):
    try:
        appid = "wx457b9d0e6f93d1c5"
        params = request.GET
        mini_openid = params.get('mini_openid')
        Log("GetBindingQRCode code:%s"%mini_openid, "local", "0.0.0.0", "DEBUG")
        wxObj = wxAccountInterface.wxAccountInterface(appid)
        res = wxObj.GetBindingQRCode(mini_openid)
        return HttpResponse(res)
    except Exception,e:
        Log("GetBindingQRCode error: %s" % e, Type="DEBUG")
        return HttpResponse(None)
    
    
def GetPoster(request):
    try:
        params = request.GET
        Log("GetPoster params:%s"%params, "local", "0.0.0.0", "DEBUG")
        appid = params.get('mini_appid',None)
        mini_openid = params.get('mini_openid',None)
        mini_product_id = int(params.get('mini_product_id',0))
        #wxuser = wxUser.objects.get(openID = mini_openid)
        res = CreateWXCodeBase64("pages/goods-details/index", mini_openid, mini_product_id)
        return HttpResponse(res,content_type='image/jpeg')
    except Exception,e:
        Log("GetPoster error: %s" % e, Type="DEBUG")
        return HttpResponse(None)
    
    
    
def GetUserPoints(request):
    try:
        params = request.GET
        #Log("GetUserPoints params:%s"%params, "local", "0.0.0.0", "DEBUG")
        mini_openid = params.get('openid',None)
        points = point_views.GetUserPoints(mini_openid)
        return HttpResponse(points)
    except Exception,e:
        Log("GetUserPoints error: %s" % e, Type="DEBUG")
        return HttpResponse(0)
    
    
def GetUserPointDetails(request):
    try:
        params = request.GET
        #Log("GetUserPoints params:%s"%params, "local", "0.0.0.0", "DEBUG")
        mini_openid = params.get('openid',None)
        user_points = point_views.GetUserPoints(mini_openid)
        detail_list = point_views.GetUserPointDetails(mini_openid)
        res = {
            "code":0,
            "data":{
                "points":user_points,
                "detail_list":detail_list
            },
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetUserPointDetails error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def SaveUserBuyMessages(request):
    try:
        params = json.loads(request.raw_post_data)
        Log("SaveUserBuyMessages params: %s" % params, "local", "0.0.0.0", "DEBUG")
        msg_id = int(params.get('msg_id',0))
        openid = params.get('openid', '')
        name = params.get('name', '')
        wxcode = params.get('wxcode', '')
        age = int(params.get('age', 0))
        grade = int(params.get('grade', 0))
        mobile = int(params.get('mobile', 0))
        Log("SaveUserBuyMessages openid: %s" % openid, "local", "0.0.0.0", "DEBUG")
        if mobile:
            wxuser = wxUser.objects.filter(openID=openid)
            if wxuser:
                wxuser[0].Mobile = mobile
                wxuser[0].save()
        res = SaveBuyerMessages(name,wxcode,age,grade,msg_id,openid)
        return HttpResponse(res)
    except Exception,e:
        Log("SaveUserBuyMessages error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def SaveBuyerMessages(name,wxcode,age,grade,msg_id=0,openid=''):
        wxuser = wxUser.objects.values("ID","Mobile").filter(openID=openid)
        if wxuser:
            UserBuyMessages.objects.filter(wxUserID=wxuser[0]['ID']).update(IsDefault=0)
        if msg_id:
            msg = UserBuyMessages.objects.get(ID=msg_id)
            msg.Name = name
            msg.wxCode = wxcode
            msg.Age = age
            msg.Grade = grade
            msg.IsDefault = 1
            msg.Updated = datetime.now()
            msg.save()
        else:
            if wxuser:
                wx_id = wxuser[0]["ID"]
                msg = UserBuyMessages(wxUserID=wx_id, Name=name, wxCode=wxcode, Age=age, Grade=grade, IsDefault=1)
                msg.save()
        return 'ok'
    
    
def GetUserBuyMessages(request):
    try:
        params = request.GET
        Log("GetUserBuyMessages params: %s" % params, "local", "0.0.0.0", "DEBUG")
        openid = params.get('openid','')
        msgs = GetBuyerMessages(openid)
        res = {
            "code":0,
            "data":{
                "msgs":msgs,
            },
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetUserBuyMessages error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
def GetBuyerMessages(openid):
    wxuser = wxUser.objects.values("ID","Mobile").filter(openID=openid)
    if wxuser:
        msg_list = []
        msgs = UserBuyMessages.objects.values("ID","wxUserID","UserID","Name","Age","Grade","wxCode","IsDefault").filter(wxUserID=wxuser[0]["ID"])
        for msg in msgs:
            msg_list.append({"ID":msg['ID'],"wxUserID":msg['wxUserID'],"UserID":msg['UserID'],"Name":msg['Name'],"Grade":msg['Grade'],"Age":msg['Age'],"wxCode":msg['wxCode'],
                             "Mobile":wxuser[0]["Mobile"], "IsDefault":msg['IsDefault']})
        return msg_list
    return []


def SetUserDefaultMessage(request):
    try:
        params = request.GET
        Log("GetUserBuyMessages params: %s" % params, "local", "0.0.0.0", "DEBUG")
        openid = params.get('openid','')
        default_id = int(params.get('default_id',0))
        wxuser = wxUser.objects.values("ID","Mobile").filter(openID=openid)
        if wxuser and default_id:
            UserBuyMessages.objects.filter(wxUserID=wxuser[0]['ID']).update(IsDefault=0)
            UserBuyMessages.objects.filter(ID=default_id).update(IsDefault=1)
        res = {
            "code":0,
            "data":{
            },
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("SetUserDefaultMessage error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
def update_wechat_order(request):
    try:
        url = 'https://api.weixin.qq.com/mall/importorder?action=add-order&access_token=%s' % GetMiniappAccessToken()
        data = {
          "order_list": [
            {
              "order_id": "001",
              "create_time": 1544194434,
              "pay_finish_time": 1544194434,
              "desc": "只要￥9.9，美国奥数队总教练为你上6堂课！",
              "fee": 890,
              "trans_id": "4200000202201812077302628279",
              "status": 3,
              "ext_info": {
                "product_info": {
                  "item_list": [
                    {
                      "item_code": "miniapp_product",
                      "sku_id": "miniapp_product",
                      "amount": 1,
                      "total_fee": 1,
                      "thumb_url": "https://tsaistorage-1254256984.cos.ap-beijing.myqcloud.com/img/20181216-%E5%8F%B0%E5%8E%86/%E5%8F%B0%E5%8E%86%20%E5%B0%81%E9%9D%A2.jpg",
                      "title": "只要￥9.9，美国奥数队总教练为你上6堂课！",
                      "desc": "只要￥9.9，美国奥数队总教练为你上6堂课！",
                      "unit_price": 1,
                      "original_price": 1,
                      "category_list": ["课程"],
                      "item_detail_page": {
                        "path": "/pages/goods-detail/index?id=5"
                      }
                    }
                  ]
                },
                "express_info": {
                  "name": "朱力",
                  "phone": "13916159092",
                  "address": "上海市闵行区宜山路2000号",
                  "price": 0,
                  "national_code": "200000",
                  "country": "中国",
                  "province": "上海市",
                  "city": "上海市",
                  "district": "闵行区",
                },
                "promotion_info": {
                  "discount_fee": 0
                },
                "brand_info": {
                  "phone": "13916159092",
                  "contact_detail_page": {
                    "path": "/pages/index/index"
                  }
                },
                "payment_method": 1,
                "user_open_id": "oFrat4os3IPoFKUuRmAdHIN48M3c",
                "order_detail_page": {
                  "path": "/pages/index/index"
                }
              }
            }
          ]
        }
        res = Post(url,data)
        return HttpResponse(res)
    except Exception,e:
        Log("update_wechat_order error:%s" % e, Type="DEBUG")
        return HttpResponse(e)
        

def update_wechat_product(request):
    try:
        url = 'https://api.weixin.qq.com/mall/importproduct?access_token=%s' % GetMiniappAccessToken()
        data = {
          "product_list": [
            {
              "item_code": "miniapp_product",
              "title": "只要￥9.9，美国奥数队总教练为你上6堂课！",
              "desc": "只要￥9.9，美国奥数队总教练为你上6堂课！",
              "category_list": ["课程"],
              "image_list": ["https://tsaistorage-1254256984.cos.ap-beijing.myqcloud.com/img/20181216-%E5%8F%B0%E5%8E%86/%E5%8F%B0%E5%8E%86%20%E5%B0%81%E9%9D%A2.jpg"],
              "src_wxapp_path": "/pages/goods-detail/index?id=5",
              "version": 200,
              "sku_list": [
                {
                  "sku_id": "miniapp_product",
                  "price": 890,
                  "original_price": 20010,
                  "status": 1,
                }
              ]
            }
          ]
        }
        res = Post(url,data)
        return HttpResponse(res)
    except Exception,e:
        Log("update_wechat_order error:%s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
def update_wechat_cart(request):
    try:
        url = 'https://api.weixin.qq.com/mall/addshoppinglist?access_token=%s' % GetMiniappAccessToken()
        data = {
          "user_open_id": "oFrat4os3IPoFKUuRmAdHIN48M3c",
          "sku_product_list": [
            {
              "item_code": "miniapp_product",
              "title": "只要￥9.9，美国奥数队总教练为你上6堂课！",
              "desc": "只要￥9.9，美国奥数队总教练为你上6堂课！",
              "category_list": ["课程"],
              "image_list": ["https://tsaistorage-1254256984.cos.ap-beijing.myqcloud.com/img/20181216-%E5%8F%B0%E5%8E%86/%E5%8F%B0%E5%8E%86%20%E5%B0%81%E9%9D%A2.jpg"],
              "src_wxapp_path": "/pages/goods-detail/index?id=5",
              "version": 100,
              "update_time": 1542868721,
              "sku_info": {
                "sku_id": "miniapp_product",
                "price": 890,
                "original_price": 20010,
                "status": 1,
                "version": 1200,
              }
            }
          ]
        }
        res = Post(url,data)
        return HttpResponse(res)
    except Exception,e:
        Log("update_wechat_cart error:%s" % e, Type="DEBUG")
        return HttpResponse(e)
        
        
def GetCampaingPage(request):
    try:
        banners = getVar("MiniappCampaignBanner")
        banner_url = banners[0].URL
        
        tags = getVar("MiniappCampaignTags")
        tag_product = getVar("MiniappCampaignTagProduct")
        mini_product = getVar("MiniappProduct")
        tag_list=[]
        for tag in tags:
            product_list=[]
            for tag_prod in tag_product:
                product = None
                for mini_prod in mini_product:
                    if tag_prod.CampaignTagID == tag.ID and mini_prod.ID == tag_prod.MiniProductID:
                        product = mini_prod
                        break;
                if product:
                    title_url = product.ProductUrl1
                    if tag_prod.TitleImg:
                        title_url = tag_prod.TitleImg
                    product_list.append({"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUName": product.SKUName, "Price": str(GetDecimal(product.Price/100.0)), 
                                          "ProductUrl1": title_url, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                                          "ProductUrl5": product.ProductUrl5, "Inventory": product.Inventory, "OriginalPrice":int(product.OriginalPrice/100.0),
                                          "CostPrice":str(GetDecimal(product.CostPrice/100.0)),"Messages":product.Messages})
            if product_list:
                tag_list.append({"ID":tag.ID,"Name":tag.Name,"ChildName":tag.ChildName,"IsSpecial":tag.IsSpecial,"Products":product_list})
        res = {
            "code":0,
            "data":{
                "banner_url":banner_url,
                "tag_list":tag_list
            },
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCampaingPage error:%s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
def GetCashbackPage(request):
    try:
        banners = getVar("MiniappCashbackBanner")
        banner_url = banners[0].URL
        
        #mini_products = MiniappProduct.objects.filter(DistributeCashback__gt=0).order_by("Order","-ID")
        mini_products = MiniappProduct.objects.filter(ID__gt=40)
        product_list=[]
        for product in mini_products:
            product_list.append({"ID":product.ID,"Name":product.Name, "ProductCode": product.Code, "SKUName": product.SKUName, "Price": str(GetDecimal(product.Price/100.0)), 
                                          "ProductUrl1": title_url, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                                          "ProductUrl5": product.ProductUrl5, "Inventory": product.Inventory, "OriginalPrice":int(product.OriginalPrice/100.0),
                                          "CostPrice":str(GetDecimal(product.CostPrice/100.0)), "Messages":product.Messages})
        res = {
            "code":0,
            "data":{
                "banner_url":banner_url,
                "product_list":product_list
            },
            "msg":"success"
        }
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCampaingPage error:%s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    