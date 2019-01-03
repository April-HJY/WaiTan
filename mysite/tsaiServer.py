# coding=utf-8
from __future__ import division  
from django.http import HttpResponse
from django.http import HttpResponseRedirect  
import hashlib, time, re
import xml.etree.ElementTree as ET  
import pylibmc as memcache
import urllib2
from base64 import *
from utils import *
import json
from django.views.decorators.csrf import csrf_exempt  
from django.utils.encoding import *
from wxAccountInterface import *
from models import *
import coupon_views

mc = memcache.Client()
    

from urllib import urlencode



@csrf_exempt    
def home(request):
    try:   
        params = request.GET
        if request.method == 'GET' and  ('code' in request.GET.keys()): 
            code = params['code']
            (accesstoken,openId) = GetWebAccessToken(code)
            userInfo = GetUserInfo(accesstoken,openId)
            username = userInfo['nickname']
            userIcon = userInfo['headimgurl']
            userGender = userInfo['sex']
            unionID = userInfo['unionid']
        if ('redirecturl' in request.GET.keys()):
            redirecturl = ('../%s?nickname=%s&headimgurl=%s&sex=%s&unionid=%s' % (params['redirecturl'],username, urllib.quote(userIcon),userGender, unionID))  
            Log (redirecturl)
            #return HttpResponseRedirect('../test/tsaireader')
        return HttpResponseRedirect(redirecturl)
    except Exception, e:
        Log("play error!%s" % e)
        username = "生菜"
        userIcon = "http://wx.qlogo.cn/mmopen/WmwqjsSBsZLOxtFibmeFoKLshjHL23vDEtkM4uKWS7j4K851NYjN6YFReAmuqrFZAcVShPylnRXGTCJwklFsSTGug77Qq6ECe/0"
        userGender = 1
        return HttpResponseRedirect('../test/tsaireader?nickname=%s&headimgurl=%s&sex=%s' % (username, urllib.quote(userIcon),userGender))
        #template = loader.get_template('tsaireader.html')
        #context = RequestContext(request, {"userName":username, "userGender":userGender,"userIcon": userIcon})
        #return HttpResponse(template.render(context))    


    
def GetWebAccessToken(code):
    code = code.encode()
    Log("Type:%s" % type(code))
    if (mc.get(code) is not None ):
        return mc.get(code)
    try:
        appID = "wx457b9d0e6f93d1c5"  #大指点课服务号
        appSecret = "aad76903fd534d020c480a160eb38171"
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
        #Log(res)
        return json.loads(res)
    except Exception, e:
        Log("Error when GetUserInfo: %s" % e)
        return None    

def wxJSWeb(request, page):
    try:   
        wxAppId = "wx457b9d0e6f93d1c5"  #大指点课服务号
        url = "http://applinzi.ddianke.com%s" % request.get_full_path()
        Log("wxJSWeb URL: %s" %url)
        wxObj = wxAccountInterface(wxAppId)
        if request.method == 'GET' and  ('code' in request.GET.keys()): 
            #Log("wxJSWeb start:", Type="DEBUG")
            code = request.GET.get("code")
            (accesstoken,openId) = GetWebAccessToken(code)
           
            userInfo = GetUserInfo(accesstoken,openId)
            #strtest = userInfo.get("nickname", "匿名用户")
            user = wxUserClass(wxAppId, openId)
            #user.wxUserData = user.SetUserInfo(userInfo)
            user.SetUserInfo(userInfo)
        else:
            redirecturl = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect"%(wxAppId,url)
            return  HttpResponseRedirect(redirecturl)
        #Log("wxJSWeb openid: %s" % openId, Type="Debug")
        

        ticket = wxObj.GetTicket("jsapi")      
        signature = wxSign(ticket, url).sign() 
        parameter = {"appid": wxAppId, "sign": signature, "ticket":ticket, "openid":openId, "name": userInfo.get("nickname", "匿名用户") }
        if WXJSWEB_OPERATOR.get(page):
            parameter.update(WXJSWEB_OPERATOR.get(page)(request, wxAppId, openId))
        #Log("UserList: %s" % userlist)
        template = loader.get_template('%s.html'% page)
        context = RequestContext(request, parameter) 
        
        return HttpResponse(template.render(context))
    except Exception, e:
        Log("wxJSWeb play error!%s" % e, Type="DEBUG")
        return HttpResponse("Error! %s" %e)
        #template = loader.get_template('tsaireader.html')
        #context = RequestContext(request, {"userName":username, "userGender":userGender,"userIcon": userIcon})
        #return HttpResponse(template.render(context))    

        
def dzUserBind(request, wxAppId, openId):
    wxObj = wxAccountInterface(wxAppId)
    return  {"userlist": wxObj}   
        

            
def verificationcode(request, wxAppId, openId):
        try:
            wx_user = wxUser.objects.filter(SourceAccount=wxAppId, openID=openId)
            if wx_user:
            	user = wx_user[0]
                if user.Subscribed != 1:
                    Log("bindusertoken 1", Type="DEBUG")
                    return {"subscribed": False}
                elif user.MobileBound:
                    #指定发送开课模板
                    wxObj = wxAccountInterface(wxAppId)
                    wxObj.CallTemplateMessage(6, openId, user.Name, '', user.Mobile or "您绑定的手机号")
                    return {"subscribed": True, "bind": True}
            Log("bindusertoken 2", Type="DEBUG")
            return {"subscribed": True, "bind": False}
        except Exception, e:
            Log("bindusertoken Error! :%s" % e, Type="DEBUG")
            
            
def subscribe_service(request, wxAppId, openId):
        try:
            wx_user = wxUser.objects.filter(SourceAccount=wxAppId, openID=openId)
            params = request.GET
            mini_openid = params.get("mini_openid",'')
            Log("subscribe_service mini_openid:%s" % mini_openid, Type="DEBUG")
            if wx_user:
            	user = wx_user[0]
                if user.Subscribed != 1:
                    return {"subscribed": False,"mini_openid":mini_openid}
                elif user.MobileBound:
                    #mini_user = wxUser.objects.filter(openID=mini_openid)
                    
                    #指定发送开课模板
                    #wxObj = wxAccountInterface(wxAppId)
                    #wxObj.CallTemplateMessage(6, openId, user.Name, '', user.Mobile or "您绑定的手机号")
                    return {"subscribed": True, "bind": True,"mini_openid":mini_openid}
                else:
                    mini_user = wxUser.objects.filter(openID=mini_openid)
                    if mini_user:
                        user.Mobile = mini_user[0].Mobile
                        user.MobileBound = 1
                        user.save()
                        return {"subscribed": True, "bind": True,"mini_openid":mini_openid}
            return {"subscribed": True, "bind": False,"mini_openid":mini_openid}
        except Exception, e:
            Log("subscribe_service Error! :%s" % e, Type="DEBUG")
            
            
def user_center(request, wxAppId, openId):
        try:
            wx_user = wxUser.objects.filter(SourceAccount=wxAppId, openID=openId)
            #Log("user_center ", Type="DEBUG")
            if wx_user:
            	user = wx_user[0]
                if user.MobileBound:
                    return {"bind": True, "nickname":user.Name, "avatar":user.Avatar}
            return {"coupons": [], "bind": False}
        except Exception, e:
            Log("getusercoupons Error! :%s" % e, Type="DEBUG")
            return {"coupons": [], "bind": False}
        
        
def customer_service(request, wxAppId, openId):
        try:
            wx_user = wxUser.objects.filter(SourceAccount=wxAppId, openID=openId)
            #Log("user_center ", Type="DEBUG")
            if wx_user:
            	user = wx_user[0]
                #if user.MobileBound:
                updateVar("question_answer")
                q = getVar("question_answer")
                return {"nickname":user.Name, "avatar":user.Avatar, "question_answer": q}
            return {"coupons": [], "bind": False}
        except Exception, e:
            Log("getusercoupons Error! :%s" % e, Type="DEBUG")
            return {"coupons": [], "bind": False}
            
            
def usercoupons(request, wxAppId, openId):
        try:
            wx_user = wxUser.objects.filter(SourceAccount=wxAppId, openID=openId)
            #Log("usercoupons ", Type="DEBUG")
            if wx_user:
            	user = wx_user[0]
                if user.MobileBound:
                    coupons = coupon_views.GetUserCoupons(user.Mobile)
                    invalid_coupons = coupon_views.GetUserInvalidCoupons(user.Mobile)
                    return {"coupons": coupons, "bind": True, "nickname":user.Name, "avatar":user.Avatar, "invalid_coupons":invalid_coupons}
            return {"coupons": [], "bind": False}
        except Exception, e:
            Log("getusercoupons Error! :%s" % e, Type="DEBUG")
            return {"coupons": [], "bind": False}
        
        
def read_count(request, wxAppId, openId):
        try:
            params = request.GET
            rd_url = params.get("rd_l", None)
            Log("read_count params %s" % params, Type="DEBUG")
            msg_info_id = params.get("msg_info_id", None)
            data = {}
            if msg_info_id:
                msg_info = MessageInfo.objects.get(ID=msg_info_id)
                Log("read_count 1", Type="DEBUG")
                msg_log = MessageLog.objects.get(OpenID = openId, MsgInfoID=msg_info_id)
                data = {'rd_url': msg_info.rd_url}
                if not msg_log.IsRead:
                    Log("read_count 1", Type="DEBUG")
                    msg_log.IsRead = 1
                    msg_log.save()
                    
                    msg_info.ReadCount += 1
                    msg_info.save()
            return data
        except Exception, e:
            Log("read_count Error! :%s" % e, Type="DEBUG")
            return {"rd_url":"http://www.ddianke.com"}
            
                    
WXJSWEB_OPERATOR = {
    "verificationcode": verificationcode,
    "usercoupons": usercoupons,
    "user_center": user_center,
    "customer_service": customer_service,
    "read_count": read_count,
    "subscribe_service": subscribe_service,
}
    
       
        
        
        