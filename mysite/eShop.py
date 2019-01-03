# coding=utf-8
from django.http import *
import hashlib, time, re
import xml.etree.ElementTree as ET  
import pylibmc as memcache
import urllib2
from utils import *
import json
from django.views.decorators.csrf import csrf_exempt  
from django.utils.encoding import *
from wxAccountInterface import *
from DefClass import *
from urllib import urlencode
from wxUtils import *    
mc = memcache.Client()
    
@csrf_exempt    
def home(request):
    try:   
        wxAppId = "wx92a26ba6653d5b56"  #生菜阅读服务号
        wxObj = wxAccountInterface(wxAppId)
        url = "http://applinzi.ddianke.com%s" % request.get_full_path()
        ticket = wxObj.GetTicket("jsapi")      
        signature = wxSign(ticket, url).sign() 
        params = request.GET
        template = loader.get_template('eshop.html')
        #user = wxUserClass()
        if request.method == 'GET' and  ('code' in request.GET.keys()): 
            code = params['code']
            (accesstoken,openId) = GetWebAccessToken(code)
            userInfo = GetUserInfo(accesstoken,openId)
            user = wxUserClass(wxAppId,openId)
            Log("userData:%s"% user.wxUserData.Name)

        context = RequestContext(request, {"userinfo":user.wxUserData, "appid": wxAppId, "sign": signature, "ticket":ticket}) 
        
        return HttpResponse(template.render(context))
    except Exception, e:
        Log("play error!%s" % e)
        return HttpResponse("Error! %s" %params)
        #template = loader.get_template('tsaireader.html')
        #context = RequestContext(request, {"userName":username, "userGender":userGender,"userIcon": userIcon})
        #return HttpResponse(template.render(context))    

        
def prepay(request):
    try:
        
        if request.method == 'POST':
            params = request.POST
            if params:
                ProductCode = params.get("ProductCode")
                Log("ProductCode: %s" % ProductCode)
                product = wxProduct.objects.filter(ProductCode=ProductCode)
                if product:
                    appid = product[0].appid
                    price = product[0].price
                    productType = product[0].ProductType
                    productName = product[0].ProductName
                    mchid = product[0].mchid
                    notifyUrl = product[0].notifyUrl
                else: # product Code not exists
                    Log("product Code not exists")
                    return -1
                quantity = params.get("quantity")
                openid = params.get("openid")
                name = params.get("name")
                phoneNum = params.get("phoneNum")
                address = params.get("address")
                prepayid = GetwxPrepayId(appid,price,quantity,ProductCode,productType,productName,openid,mchid,notifyUrl,name,phoneNum,address)
                Log("prepayid generated: %s" % prepayid)
                return HttpResponse("%s"%prepayid)
            else: #params is None
                return -1
        else:
            return HttpResponseForbidden()
    except Exception, e:
        Log("GenerateOrder error!%s" % e)
        return HttpResponse("Error! %s" %e)
    
def GetWebAccessToken(code):
    code = code.encode()
    Log("Type:%s" % type(code))
    #if (mc.get(code) is not None ):
    #    return mc.get(code)
    try:
        appID = "wx92a26ba6653d5b56"  #s生菜阅读服务号
        appSecret = "cb08af31b7b137bf7ecef9b5a548e4ba"
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (appID, appSecret, code)
        response = urllib2.urlopen(url) 
        res = response.read().decode("utf8") 
        Log(res)
        resJson = json.loads(res)
        mc.set(code,  (resJson['access_token'], resJson['openid']))
        return (resJson['access_token'], resJson['openid'])
    except Exception, e:
        Log("Error when GetWebAccessToken: %s" % e)
        return None        

def GetUserInfo(accesstoken, openid):
    try:
        #accesstoken = self.GetAccessToken()
        url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (accesstoken, openid)
        response = urllib2.urlopen(url) 
        res = response.read().decode("utf8") 
        Log(res)
        return json.loads(res)
    except Exception, e:
        Log("Error when GetUserInfo: %s" % e)
        return None    
        

