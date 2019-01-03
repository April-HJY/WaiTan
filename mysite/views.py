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
import ssl
import mimetypes
from tsaiPlatform import *
from wxUtils import * 
from django.db.models import Q
import pymysql
import os
from Crypto.Cipher import AES
import talk_cloud_interface
import AESCipher
import import_views
import student_views
import point_views
import coupon_views
#import requests


def home(request):
        
        template = loader.get_template('Homepage.html')
        context = RequestContext(request, {"Info":mc.get("ticket")})
        return HttpResponse(template.render(context))

       
    
def register(request):
        
        template = loader.get_template('Register.html')
        context = RequestContext(request, {"Info":"Hello World!"})
        return HttpResponse(template.render(context))

def test(request, page):
        template = loader.get_template('%s.html'%page)
        parameter = {}
        #if TESTWEB_OPERATOR.get(page):
        #    parameter.update(WXJSWEB_OPERATOR.get(page)(request))
        #Log("UserList: %s" % userlist)
        context = RequestContext(request, parameter)
        return HttpResponse(template.render(context))


#TESTWEB_OPERATOR = {"binduser": binduser}

def sales(request):
        
        template = loader.get_template('sales.html')
        context = RequestContext(request, {"Info":"Hello World!"})
        return HttpResponse(template.render(context))
    
def step1(request):
        #workObj = wxAccountInterface.wxAccountInterface("wx3a6ed5af1b0f81d6")
        #res = workObj.GetNewsList(0,10)
        #workObj.AddNewsList(res)
        
        #Log("Test Log: %s" % res, Type="DEBUG")  
        #Log("GetToken: %s" % workObj.GetAccountToken())
        #workObj.updateVar("wxTicket_jsapi")
        #res = workObj.RefreshUserList()
        #Log("boy_list"% mc.get("boy_list"))
        wxObj = wxAccountInterface.wxAccountInterface('wx92a26ba6653d5b56')
        Log("wxObj Config: %s" % wxObj.GetConfig())

        
        Info = ""
        total = 3000
        for i in range(1,12):
            start = total/(13-i) - 100
            end = total/(13-i) + 100
            x = random.randint(start, end)
            Info =  "%s\n%s" %(Info,x)
            total = total- x
            
             
        
        template = loader.get_template('step1.html')
        context = RequestContext(request, {"Info":Info})
        response = HttpResponse(template.render(context))
        response.set_cookie("Testcookie", "Hello!")

        return response

def CRM(request):
        toUser = mc.get("toUser")
        text = mc.get("text")
        if (toUser is not None and text is not None):
            SendMsg(toUser,text)
            return "success"
        else:
            return "Not Send due to none user or text." 
def Marathon(request):
        #RefreshMarathon()
        allMarathon = Sheet1.objects.all() 
        template = loader.get_template('URLMonitor.html')
        context = RequestContext(request, {"ItemList":allMarathon}) 
        return HttpResponse(template.render(context))
        
def RefreshIndex(request):
        try:
            Log("Start RefreshIndex!")
            AllAccounts = getVar("AllWxAcounts")
            #Log("AllAccounts: %s" % AllAccounts )
        #wxObj = getVar("wxObjTsaiReader")
        #wxObj.updateVar("wxTicket_jsapi")
            for c in AllAccounts:
                workObj = wxAccountInterface.wxAccountInterface(c.appId)
                #Log("Data: %s" % workObj.wxData.appName)
                workObj.BuildIndex()
            #workObj.BuildMenu()
            
            
            
            return HttpResponse("success")
        except Exception, e:
            Log("RefreshIndex Error: %s" % e)
            return HttpRespnse("error: %s" % e)

#tsaiPlatform只能获得web端拿到的信息，无法处理小程序，所以暂时闲置
def UpdateUsersInfo():
    try:
        miniappID = 'wx0c0e0edd8eaad932'
        wxUsers = wxUser.objects.filter(Avatar = '', SourceAccount=miniappID)
        if len(wxUsers) > 0:
            tsaiObj = tsaiPlatform()
            #token = tsaiObj.GetAccessToken()
            for user in wxUsers:
                if user.openID != '':
                    Log("UpdateUsersInfo openID:%s" % user.openID,"local", "0.0.0.0", "DEBUG")
                    userInfo = tsaiObj.GetUserInfo( user.openID)
                    Log("UpdateUsersInfo userInfo: %s" % userInfo,"local", "0.0.0.0", "DEBUG")
                break
    except Exception, e:
        Log("UpdateUsersInfo Error: %s" % e,"local", "0.0.0.0", "DEBUG")

def authority(request):
        
        tsaiObj = tsaiPlatform()
        
        pre_auth_code = tsaiObj.GetPreAuthCode()
        authURL = "https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid=" + tsaiObj.appId + "&pre_auth_code=" + pre_auth_code + "&redirect_uri=http://applinzi.ddianke.com/deny"     
        response = HttpResponseRedirect(authURL)
        response['Referral'] = "http://applinzi.ddianke.com"
        return response

def index(request):
        publicAppID = ''
        if request.method == 'GET': 
            params = request.GET
            if params.has_key('appid'):
                publicAppID = params['appid']
        HotArticles = getVar("HotArticles")
        LatestArticles = getVar("LatestArticles")
        AllWxAcounts = getVar("AllWxAcounts")
        Log("AllWxAcounts:%s"%len(AllWxAcounts))
        MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
        #if (MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT'])):
        #    template = loader.get_template('authority.html')
        #else: 
        template = loader.get_template('login.html')
        wxUserCount = getVar("wxUserCount")
        wxNewsCount = getVar("wxNewsCount")
        Log("User Agent:%s"%request.META['HTTP_USER_AGENT'])
 
        #authURL = "http://applinzi.ddianke.com/authority/"     
        tsaiObj = tsaiPlatform()
        
        pre_auth_code = tsaiObj.GetPreAuthCode()
        authURL = "https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid=" + tsaiObj.appId + "&pre_auth_code=" + pre_auth_code + "&redirect_uri=http://applinzi.ddianke.com/deny"     

        context = RequestContext(request, {"Articles":LatestArticles,"Info":authURL, "wxAccounts": AllWxAcounts, "wxUserCount": wxUserCount, "wxNewsCount": wxNewsCount, "publicAppID":publicAppID, 
                                           "IsMobile":  MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT'])})
        return HttpResponse(template.render(context))

    
def callback(request):
        
        if request.method == 'GET': 
            params = request.GET
            url = params['auth_code']
        template = loader.get_template('Homepage.html')
        context = RequestContext(request, {"Info": url})
        return HttpResponse(template.render(context))

@csrf_exempt 
def articles(request):
    
            articleID = 0
        #try:
            if "UserName" in request.COOKIES:  
                strUsername = request.COOKIES["UserName"]
            else:
                strUsername = GetUserName()
                Log("Ramdomized!")
            
            if request.method == 'GET': 
                params = request.GET
                intArticleID = params['id']
            if request.method =='POST':
            
                params = request.POST
                Log("Post data!%s"%params)
                if (params['ChangeName'] == '1'):
                    strUsername = GetUserName()
                else:
                    strUsername = params['author']
                strContent = params['content']
                intArticleID = params['articleID']
                c = Comment(ArticleID = intArticleID, content = strContent, UserName = strUsername, PostDate = datetime.datetime.now())
                c.save()
                
                updateVar(str("comments#" + intArticleID))
            
            c = getVar(str("article#"+intArticleID))
            if (len(c)>0):
                c = c[0]
            else:
                c= None
            #strTest = "comments_%s" % intArticleID
            comments = getVar(str("comments#" + intArticleID))
            #Log(comments)
            #username = GetUserName()
            template = loader.get_template('Article.html')
            context = RequestContext(request, {"article": c, "articleURL": c.ArticleURL.rstrip("#rd"), "comments":comments, "UserName": strUsername, "articleID": intArticleID })
            response = HttpResponse(template.render(context))
            response.set_cookie("UserName", strUsername)
       # except Exception, e:
       #     Log("Error : %s" % e)
       #     template = loader.get_template('Article.html')
       #     context = RequestContext(request)
       #     response = HttpResponse(template.render(context))
            return response
    
@csrf_exempt
def AccountArticles(request):
    Log("AccountArticles")
    pageSize = 10
    try:
        if request.method == 'GET': 
            Log("AccountArticles GET")
            params = request.GET
            if params.has_key('appid'):
                appid = params['appid']
                if params.has_key('page'):
                    page = int(params['page'])
                else:
                    page = 1
                Log("AccountArticles appid%s"%appid)
                auth = getVar("AllWxAcounts").filter(appId = appid)[0]
                articles = Articles.objects.filter(SourceAccount = auth.appName)
                returnArticles = []

                start = pageSize * (page - 1)
                articleCount = len(articles)
                pageCount = articleCount / pageSize + 1
                if pageSize * page > articleCount:
                    end = articleCount
                else:
                    end = pageSize * page
                #Log("start:%d end:%d" % (start, end), "local", "0.0.0.0", "DEBUG")    
                for i in range(start, end):
                    x = {"URL":articles[i].ArticleURL, "Author": articles[i].Author, "Title": articles[i].Title}
                    returnArticles.append(x)
                resJSON = json.dumps({"articles":returnArticles, "pageCount":pageCount, "currPage":page})
                Log("AccountArticles resJSON%s"%resJSON)
                return HttpResponse(resJSON)
            
        return None
    except Exception, e:
        Log("AccountArticles Error: %s" % e)
        return HttpResponse(e)
        
def login(request):
    template = loader.get_template('QRCodePage.html')
    url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx92a26ba6653d5b56&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect" % ("http%3A%2F%2Fapplinzi.ddianke.com%2FUserLogin%2F" , "state")
    context = RequestContext(request, {"url": url, "msg":"扫码登陆" })
    return HttpResponse(template.render(context))
       

def Accounts(request):
    	Log("Accounts")
      	appid = "wx3a6ed5af1b0f81d6" 
        
        try:
            
                        
            if request.method == 'GET': 
                params = request.GET
                if params.has_key('appid'):
                    appid = params['appid']
                Log("Accounts appId:%s"%appid)
            accounts = wxAccounts.objects.filter(appId = appid)            
            configs = getAccountConfig(appid)
            imageList = []
            if len(accounts) > 0:
                account = accounts[0]
            template = loader.get_template('wxAccounts.html')
                                
            context = RequestContext(request, {"Account": account, "ImageList":imageList, "Configs":configs })
            return HttpResponse(template.render(context))
        except Exception, e:
            Log("Error:%s"%e)
            
def AccountView(request):
    	Log("AccountView")
      	appid = "wx3a6ed5af1b0f81d6" 
        tsaiObj = tsaiPlatform()
        try:
            if request.method == 'GET': 
                params = request.GET
                if params.has_key('appid'):
                    appid = params['appid']
                    Log("AccountView get appId:%s"%appid)
                if params.has_key('update'):
                    Log("AccountView update :%s"%appid)
                    accountInterface = tsaiObj.GetwxAccountInterface(appid) 
                    Log("AccountView accountInterface :%s"%appid)
                    configs = accountInterface.GetConfig()
                    Log("AccountView xx :%s"%configs)
                    for config in configs['configlist']:
                        Log("AccountView config :%s"%config['configName'])
                        if params.has_key(config['configName']):
                            config['configValue'] = params[config['configName']]
                	Log("AccountView configs :%s"%configs)
                	accountInterface.SaveConfig(configs)
            
            accountInterface = tsaiObj.GetwxAccountInterface(appid) 
            configs = accountInterface.GetConfig()
            accounts = wxAccounts.objects.filter(appId = appid)
            
            if len(accounts) > 0:
                account = accounts[0]
                
            template = loader.get_template('AccountView.html')
            context = RequestContext(request, {"Account": account, "Configs": configs['configlist'] })
            return HttpResponse(template.render(context))
        except Exception, e:
            Log("AccountView Error:%s"%e)
            

def AccountSettings(request):
    	Log("AccountSettings")
      	appid = "wx3a6ed5af1b0f81d6" 
        tsaiObj = tsaiPlatform()
        try:
            if request.method == 'GET': 
                params = request.GET
                if params.has_key('appid'):
                    appid = params['appid']
                    Log("AccountSettings get appId:%s"%appid)
                if params.has_key('update'):
                    Log("AccountSettings update :%s"%appid)
                    accountInterface = tsaiObj.GetwxAccountInterface(appid) 
                    Log("AccountSetting accountInterface :%s"%appid)
                    configs = accountInterface.GetConfig()
                    Log("AccountSettings xx :%s"%configs)
                    for config in configs['configlist']:
                        Log("AccountSettings config :%s"%config['configName'])
                        if params.has_key(config['configName']):
                            config['configValue'] = params[config['configName']]
                	Log("AccountSettings configs :%s"%configs)
                	accountInterface.SaveConfig(configs)
            
            accountInterface = tsaiObj.GetwxAccountInterface(appid) 
            configs = accountInterface.GetConfig()
            accounts = wxAccounts.objects.filter(appId = appid)
            
            if len(accounts) > 0:
                account = accounts[0]
                
            template = loader.get_template('AccountSetting.html')
            context = RequestContext(request, {"Account": account, "Configs": configs['configlist'] })
            return HttpResponse(template.render(context))
        except Exception, e:
            Log("AccountSettings Error:%s"%e)
            
            
@csrf_exempt       
def UpdateAccountConfig(request):
    	Log("UpdateAccountConfig")
        try:
            if request.method == 'POST': 
                
                params = request.POST
                if params.has_key('appid'):
                    appid = params['appid']
                Log("Update Account Config appId:%s"%appid)           
    
                defaultConfigs = DefaultConfig.objects.filter(Enable = 1).order_by("ConfigOrder")
                for c in defaultConfigs:
                    if params.has_key(c.ConfigName):
                        configs = wxConfig.objects.filter(appid = appid, ConfigName = c.ConfigName)
                        
                        value = params[c.ConfigName]
                        if len(configs) > 0:
                            config = configs[0]
                            config.ConfigValue = value
                            config.save()
                        else:
                            config = wxConfig(appid = appid, ConfigName = c.ConfigName, ConfigValue = c.ConfigValue)
                            config.save()
            return  HttpResponse("success")
            #accounts = wxAccounts.objects.filter(appId = appid)   
            #configs = getAccountConfig(appid)
            #imageList = []
            #if len(accounts) > 0:
            #    account = accounts[0]
            template = loader.get_template('UpdateAccountConfig.html')
                                
            context = RequestContext(request, {"appid": appid })
            return HttpResponse(template.render(context))
        except Exception, e:
            Log("Error:%s"%e)

@csrf_exempt
def scheduler(request):
    
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
            ip =  request.META['HTTP_X_FORWARDED_FOR']  
        else:  
            if request.META.has_key('REMOTE_ADDR'):
                ip = request.META['REMOTE_ADDR']  
    	LogPV(request)
        try:
            if request.GET.has_key('IsEdit'):
                EditMode = True
            else:
                EditMode = False
            if request.method == 'POST':
                params = request.POST
                postDate = getBlankDayRecently()
                
                if params.has_key('PostID'):
                    id = params['PostID']
                    if params.has_key('PostDate'):
                	    postDate = params['PostDate']
                    postExpired = 0
                    if params.has_key('PostExpired'):
                        postExpired = params['PostExpired']
                    Log("Expired %s" % postExpired)
                    s = Schedule.objects.get(ID = id)
                    if s is not None:
                        #if len(postDate) > 0:
                        #    s.ScheduleDate = postDate
                        s.Expired = postExpired
                        s.Editor = params['PostEditor']
                        s.save()
                        Log("Change Date PostID:%s " % id , Type="DEBUG")
                    else:
                        Log("Has not PostID:%s " % id , Type="DEBUG")
                else:
                    Log("new schedule")
                    urlTitlePic = ""
                    urlRewardCode = ""
                    randomCode = random_str(16)
                    Log(randomCode)
                    if request.FILES.has_key("titlePicture"):
                        Log("titlePicture")
                        titlePicture = request.FILES["titlePicture"]
                        urlTitlePic = UploadFile("生菜阅读_" +  titlePicture.name, titlePicture)
                        if urlTitlePic == "oversize":
                            urlTitlePic = ""
                    if request.FILES.has_key("rewardCode"):
                        Log("rewardCode")
                        rewardCode = request.FILES["rewardCode"]
                        urlRewardCode = UploadFile("RewardCode" +  rewardCode.name, rewardCode)
                        if urlRewardCode == "oversize":
                            urlRewardCode = ""
                    Log("PostData:%s"%params)
                    if params["urlLink"] == "" and params["content"] == "" and urlTitlePic == "":
                        return HttpResponse("写点东西吧:)")
                    openid = ''
                    if params.has_key("openID"):
                        openid = params["openID"]
                    articleType = ''
                    if params.has_key("articleType"):
                        articleType=params["articleType"]
                    c = Schedule(Author = params["author"], AuthorBio = params["authorBio"],ScheduleDate = postDate,ArticleURL = params["urlLink"], ArticleContent = params["content"], 
                                 Title=params["title"],TitlePicture = urlTitlePic,RewardCode = urlRewardCode, openID = openid, ArticleType = articleType)
                    c.save()
                updateVar("Schedule")

               # {u'': [u'\u5176\u5b9e\u5c31\u662f\u6211\u5566'], u'URL': [u'http://www.teni.com'], u'PostDate': [u'2015-05-02'], u'content': [u'test'], u'author': [u'\u5c0f\u751f\u624d']}
        except Exception, e:
                Log("Error:%s"%e, Type="DEBUG")
                       
            #return  HttpResponse("success")    
        #c = Schedule(Author = "author", AuthorBio = "authorBio",ScheduleDate = "2015-6-5",ArticleURL = "http://test", ArticleContent = "content")
        #c.save()
        AllArticles = getVar("Schedule")
        wxAppId = "wx92a26ba6653d5b56"  #生菜阅读服务号
        wxObj = wxAccountInterface.wxAccountInterface(wxAppId)
        url = "https://applinzi.ddianke.com%s" % request.get_full_path()
        ticket = wxObj.GetTicket("jsapi")  
        #Log("ticket:%s" % ticket, Type="DEBUG")
        signature = wxSign(ticket, url).sign() 
        #Log("signature:%s" % signature, Type="DEBUG")
        params = request.GET
        #user = wxUserClass()
        if request.method == 'GET' and  ('code' in request.GET.keys()): 
            code = params['code']
            (accesstoken,openId) = GetWebAccessToken(code)
            userInfo = GetUserInfo(accesstoken,openId)
            user = wxUserClass(wxAppId,openId)
            
        if request.method == 'GET' and  ('openId' in request.GET.keys()): 
            openId = params['openId']
            Log("openid:%s"%openId, Type="DEBUG")

        context = RequestContext(request, {}) 
        
        #Log("PageView:%s"% PageLog.objects.values('ID').filter(URL__icontains = "/calendar/").count())
        MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
        if (MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT'])):
            template = loader.get_template('Scheduler_WX.html')
        else: 
            template = loader.get_template('Scheduler.html')
        
        context = RequestContext(request, {"Articles": AllArticles, "EditMode":EditMode,  "appid": wxAppId, "sign": signature, "ticket":ticket, "PageView": PageLog.objects.filter(URL__icontains = "/calendar/").count})
        return HttpResponse(template.render(context))
    


def GetWebAccessToken(code):
    code = code.encode()
    Log("Type:%s" % type(code))
    if (mc.get(code) is not None ):
        return mc.get(code)
    try:
        appID = "wx92a26ba6653d5b56"  #生菜阅读服务号
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
        return res
    except Exception, e:
        Log("Error when GetUserInfo: %s" % e)
        return None    
        

        
    
@csrf_exempt
def Coat(request):
        
        #return HttpResponse("第一批站衫预订已经结束，请留意水源Juhui板关注后续信息") 
        
                    #return HttpResponse("/PayBill?prepay_id = %s" % prepay_id )
               # c = OITM(ProductName = params["author"], Size = params["authorBio"],Color = params["PostDate"],Quantity = params["urlLink"], TotalAmount = params["content"], wxPayURL=, BBSID=,Name=, Tel=, Address=)
               # c.save()
               # {u'': [u'\u5176\u5b9e\u5c31\u662f\u6211\u5566'], u'URL': [u'http://www.teni.com'], u'PostDate': [u'2015-05-02'], u'content': [u'test'], u'author': [u'\u5c0f\u751f\u624d']}
            #return  HttpResponse("success")    
        #c = Schedule(Author = "author", AuthorBio = "authorBio",ScheduleDate = "2015-6-5",ArticleURL = "http://test", ArticleContent = "content")
        #c.save()
        #AllArticles = Schedule.objects.filter(Expired = 0).order_by("ScheduleDate")
        wxAppId = "wx457b9d0e6f93d1c5"
        ticket = ""
        signature = ""
        url = "http://applinzi.ddianke.com/CrystalCrab/"
        if len(wxAccounts.objects.filter(appId = wxAppId))>0:
            wxObj = wxAccountInterface.wxAccountInterface(wxAppId)
            ticket = wxObj.GetTicket("jsapi")      
            signature = wxSign(ticket, url).sign()   
            cardTicket = wxObj.GetTicket("wx_card")
            cardSign = wxCardSign(cardTicket,wxAppId).sign()
        template = loader.get_template('Coat.html')
        context = RequestContext(request, {"appid": wxAppId, "sign": signature, "ticket":ticket, "cardTicket": cardTicket, "cardSign":cardSign })
        return HttpResponse(template.render(context))    

@csrf_exempt 
def PayBill(request):
        try:
            
            wxAppId = "wx92a26ba6653d5b56"  #生菜阅读服务号
            wxObj = wxAccountInterface.wxAccountInterface(wxAppId)
            #Log("Step: 1")
            url = "https://applinzi.ddianke.com%s" % request.get_full_path()
            ticket = wxObj.GetTicket("jsapi")      
            signature = wxSign(ticket, url).sign() 
            params = request.GET
            #Log("Step: 2")
            #user = wxUserClass()            
            if request.method == 'GET': 
                params = request.GET
                Log("Paybill params: %s"%params)
                if "prepay_id" in params.keys():
                    prepay_id = params["prepay_id"]
                    c = OITM.objects.filter(PrePay_ID = prepay_id)[0]
                if "TradeNumber" in params.keys():
                    trade_number = params["TradeNumber"]
                    c = OITM.objects.filter(TradeNumber = trade_number)[0]
 
            payinfo = wxPaySign(wxAppId,prepay_id).sign()
            Log ("PayInfo: %s" % payinfo)
            template = loader.get_template('PayBill.html')
            context = RequestContext(request,  {"appid": wxAppId, "sign": signature, "ticket":ticket, "OITM": c, "payinfo": payinfo, "TotalAmount": c.TotalAmount/100})
            return HttpResponse(template.render(context))
        except Exception, e:
            Log("Error:%s"%e)

@csrf_exempt            
def PaidCallback(request):
        try:
            c=None
            if request.method == 'POST':
                Log("PaidCallback PostData:%s"%request.raw_post_data, Type="DEBUG")
                xml = ET.fromstring(request.raw_post_data)
                out_trade_no = xml.find("out_trade_no").text
                transaction_id = xml.find("transaction_id").text
                c=OITM.objects.filter(TradeNumber = out_trade_no)[0]
                c.Paid =1
                c.TransactionID = transaction_id
                c.save()
                trade = TradeInfo.objects.filter(TradeID=out_trade_no)
                user = User.objects.filter(Mobile=c.Mobile)
                thirdparty = LessonsOfThirdParty.objects.filter(ProductID=c.ProductID,ChannelID=c.ChannelID)
                wxuser = wxUser.objects.get(openID = c.PaidOpenId)
                if user and not trade:
                    SaveFormid(c.PaidOpenId, c.PrePay_ID, user[0].Name, True)
                    rate = GetUserPointRate('paid')
                    import_views.CreateTrade(c.Mobile, user[0].Name, out_trade_no, c.ProductName, c.ChannelID, c.TotalAmount/100.0, 'weixin', c.SKU, c.ID)
                    paid_point = round(c.TotalAmount*rate.Rate/100)
                    if paid_point == 0:
                        paid_point = 1
                    point_views.UpdatePointToUser(wxuser.ID, paid_point, object_type='OITM', object_id=c.ID, reason=rate.Name) 
                    #Log ("PaidCallback 0", Type="DEBUG")
                    if c.DistributorID:
                        #Log ("PaidCallback 1", Type="DEBUG")
                        product = MiniappProduct.objects.filter(ID=c.ProductID)
                        if product:
                            #Log ("PaidCallback 2", Type="DEBUG")
                            product = product[0]
                            rate = GetUserPointRate('distribute')
                            distribute_point = 0
                            if product.DistributePoint:
                                distribute_point = product.DistributePoint
                            elif round(c.TotalAmount*rate.Rate/100) > 0:
                                distribute_point = round(c.TotalAmount*rate.Rate/100)
                            else:
                                distribute_point = 1
                            point_views.UpdatePointToUser(c.DistributorID, distribute_point, object_type='OITM', object_id=c.ID, reason=rate.Name)    
                                
                    if c.PaidPoints:
                        wxuser = wxUser.objects.filter(openID = c.PaidOpenId)
                        if wxuser:
                            point_views.UpdatePointToUser(wxuser[0].ID, (0-c.PaidPoints), object_type='OITM', object_id=c.ID, reason='消费')
                    #thirdparty_id = None
                    #cate_id = 5
                    #if thirdparty:
                    #    thirdparty_id = thirdparty[0].ID
                    #    cate_id = thirdparty[0].LessonCategoryID
                    #trade = TradeInfo(TradeID=out_trade_no,UserID=user[0].ID,IsImported=1,ChannelID=c.ChannelID,OrderCount=1,Name=c.ProductName,TradeType='wexin',BuyerMessage=c.Messages,OuterTradeID=c.ID,
                    #                  TransactionID=transaction_id,TotalFee=c.TotalAmount/100.0,Payment=c.TotalAmount/100.0,PayType='wexin',ProdID=c.ProductID,SKUName=c.SKU,ProdCount=1,
                    #                 ThirdPartyID=thirdparty_id,LessonCategoryID=cate_id, DistributorName=None, DistributorID=None, DistributorType=None, Relations=None)
                    #trade.save()
                #ProductCode = c.ProductCode
                #obj = getVar('wxProduct').filter(ProductCode = ProductCode)[0]
                #tickets_sold = OITM.objects.filter(ProductCode=ProductCode).filter(Paid=1).count()
                #if tickets_sold > 50:
                #    price = 3500 + (tickets_sold-50) * 50
                
                #obj.price = price
                #    obj.save()
                
            return HttpResponse("success")
        except Exception, e:
            Log ("PaidCallback Error:%s"%e, Type="DEBUG")
            return HttpResponse(e)
        
        
@csrf_exempt            
def RefundCallback(request):
        try:
            c=None
            if request.method == 'POST':
                Log("RefundCallback PostData:%s"%request.raw_post_data, Type="DEBUG")
                xml = ET.fromstring(request.raw_post_data)
                key = 'IGWCHdS58OGbH4OkM1MIL9ZyV6QDQ1hp'
                #ProductCode = c.ProductCode
                #obj = getVar('wxProduct').filter(ProductCode = ProductCode)[0]
                #tickets_sold = OITM.objects.filter(ProductCode=ProductCode).filter(Paid=1).count()
                #if tickets_sold > 50:
                #    price = 3500 + (tickets_sold-50) * 50
                
                #obj.price = price
                #    obj.save()
                
            return HttpResponse("success")
        except Exception, e:
            Log ("RefundCallback Error:%s"%e, Type="DEBUG")
            return HttpResponse(e)
            
            
def PayDone(request):
        try:
            c=None
            if request.method == 'GET': 
                params = request.GET
                Log("PayDone params: %s"%params)
                if "TradeNumber" in params.keys():
                    TradeNumber = params["TradeNumber"]
                    c = getVar('OITM').filter(TradeNumber = TradeNumber)[0]
            template = loader.get_template('PayDone.html')
            context = RequestContext(request, {"OITM": c })
            return HttpResponse(template.render(context))    
        except Exception, e:
            Log("PayDone Error:%s" %e)
            
#upload test
#don't use this method
def upload(request):
    Log("upload")
    urlTitlePicture = ""
    urlRewardCode = ""
    if request.method == 'POST':
        Log("POST")
        if request.FILES.has_key('titlePicture'):
            Log("TitlePicture has key")

            content = request.FILES['titlePicture']
            urlTitlePicture = UploadFile("TitlePicture_" + content.name, content)
            Log("TitlePicture url %s" % urlTitlePicture)
        if request.FILES.has_key('rewardCode'):
            Log("rewardCode has key")
            content = request.FILES['rewardCode']
            urlRewardCode = UploadFile("RewardCode_" + content.name, content)
            Log("rewardCode url %s" % urlRewardCode)
    if urlTitlePicture == "oversize":
    	Log("titlePicture oversize")
    if urlRewardCode == "oversize":
    	Log("rewardCode oversize")
    template = loader.get_template('upload.html')
    context = RequestContext(request, {"urlTitlePicture": urlTitlePicture, "urlRewardCode":urlRewardCode})
    return HttpResponse(template.render(context)) 
        
            
            
def storagefiles(request):
    Log("storagefiles")
    if request.method == 'POST':
        DeleteFileFromStorage(request.POST["fileName"])
    fileList = GetAllFilesOfStorage()
    template = loader.get_template('storagefiles.html')
    context = RequestContext(request, {"fileList": fileList})
    return HttpResponse(template.render(context))

            
@csrf_exempt
def Import(request):
    Log('Import')
    updateVar("Schedule");
    postUrl = "http://42.96.204.200/import/index.php"
    if request.method == 'POST':
        params = request.POST
        if params.has_key('url'):
            try:
                url = params['url']
                author = params['author']
                authorBio = params['authorBio']
                values ={"url": url}
                s = urllib.urlencode(values)
                req = urllib2.Request(postUrl + "?" + s)
                response = urllib2.urlopen(req)
                decodejson = json.loads(response.read())
                if decodejson['status'] == 200:
                    Log("Title:%s"%decodejson['title'])
                    postDate = getBlankDayRecently()
                    content = decodejson['data'][0]
                    for i in range(0, len(decodejson['data'])):
                        Log("content:%s"%decodejson['data'][i])
                    #c = Schedule(Author = author, AuthorBio = authorBio,ScheduleDate = postDate, ArticleContent = content.encode(), ArticleURL = url, Title=decodejson['title'],TitlePicture = "",RewardCode = "")
                    #try:
                    #    c.save()
                    #except Exception, e:
                    #    Log( "Error when Save: %s"%e)
                    
                    #updateVar("Schedule")
                    #AllArticles = getVar("Schedule")
                    #template = loader.get_template('Scheduler.html')
                    #context = RequestContext(request, {"Articles": AllArticles, "EditMode":False, "PageView": PageLog.objects.filter(URL__icontains = "/calendar/").count})
                    #return HttpResponse(template.render(context))
                    return HttpResponse('ok')
                else:
                    Log("status:%s"%decodejson['status'])
                return HttpResponse (decodejson['title'])
            except Exception, e:
                Log( "Error when Import: %s"%e)
                return HttpResponse('error')
    else:
        template = loader.get_template('import.html')
        context = RequestContext(request)
        return HttpResponse(template.render(context)) 


def SaveMaterial(token, media, mediaType, content):
    url = "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=" + token + "&type=" + mediaType;
    #content += "\r\n"
    #values = {media:content}
    #data = json.dumps(values,ensure_ascii=False)

    #Log("Values:%s, IsUnicode:%s" % (data,isinstance(data, unicode) ))
    values = {'Content-Disposition':'form-data', 'filename':'d3hfZm10PWpwZWcraHR0cDovL21wLndlaXhpbi5xcS5jb20vcz9fX2Jpej1Nak01TWpJM05EZzJNQT09Jm1pZD0yMDkyMzU5NzImaWR4PTEmc249NmRkMTlmMGRkM2U0MzQ4MTQ4MDQ3ZDYzNzM0M2I1ODkmc2NlbmU9MA==.jpg', 
              'filelength':len(content), 'Content-Type':'image/jpg', 'content':content}
    data = urllib.urlencode(values)
    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)
    
    #LIMIT = '----------lImIt_of_THE_fIle_eW_$'
    #CRLF = '\r\n'
    #L = []
    #L.append('--' + LIMIT)
    #L.append('Content-Disposition: form-data; name="uploadfile"; filename="th.jpg"')
    #L.append('Content-Type: application/octet-stream' )
    #L.append('')
    #L.append(content)
    #L.append('--' + LIMIT + '--')
    #L.append('')
    #body = CRLF.join(L)
    #content_type = 'multipart/form-data; boundary=%s' % LIMIT
    #h = httplib.HTTP(url)
    #h.putrequest('POST', selector)
    #h.putheader('content-type', content_type)
    #h.putheader('content-length', str(len(body)))
    #h.endheaders()
    #h.send(body)
    
    
    http_header = {
                "Content-Type" : "multipart/form-data; boundary=\r\n",
"X-Requested-With" : "XMLHttpRequest",
"Referer" : "http://applinzi.ddianke.com/",
"Accept-Language" : "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
"Accept-Encoding" :	"gzip, deflate",
"User-Agent" : "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; Touch; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; InfoPath.3)",
"Host" : "applinzi.ddianke.com",
"DNT" : "1",
"Connection" : "Keep-Alive",
"Cache-Control" : "no-cache"
}
    req = urllib2.Request(url, data, http_header)
    Log("req")
    response = urllib2.urlopen(req)
    Log("response")
    return response



@csrf_exempt       
def RoleSetting(request):
    Log("RoleSetting" + request.method)
    try:
        Log("Get Role ")
        roles = getVar("Role")
        auths = getVar("Authority")

        template = loader.get_template('RoleSetting.html')

        context = RequestContext(request, {"roles": roles, "auths": auths })
        
        return HttpResponse(template.render(context))
        #return HttpResponse('ok')
    except Exception, e:
        Log("RoleSetting Error:%s"%e)
        return HttpResponse(e)

    

@csrf_exempt
def RoleSettingOperation(request):
    Log("RoleSettingOperation")
    try:
        params = request.GET
        if params.has_key('update'):
            id = params["ID"]
            Log("Update Role id:" + id) 
            s = Role.objects.get(ID = id)
            if s is not None:
                s.RoleName =  params["RoleName"]
                s.Description = params["Description"]
                s.Authorities = params["Authorities"]
                s.save()
                Log("Change PostID:%s " % id)
            else:
                Log("Has not PostID:%s " % id)
        elif params.has_key('add'):
            Log("Add Role ")  
            c = Role(RoleName = params["RoleName"], Description = params["Description"],Authorities = params["Authorities"])
            c.save()
        else:
            id = params["ID"]
            Log("Delete Role id:" + id) 
            s = Role.objects.get(ID = id)
            s.delete()
        updateVar("Role")
        return HttpResponse('ok')
    except Exception, e:
        Log("RoleSettingOperation Error:%s"%e)
        return HttpResponse(e)
    
    
@csrf_exempt       
def AuthoritySetting(request):
    Log("AuthoritySetting")
    try:
        #Log("Get Authority ", "local", "0.0.0.0", "DEBUG")
        auths = getVar("Authority")
        authsType = getVar("AuthorityType")

        template = loader.get_template('AuthoritySetting.html')

        context = RequestContext(request, { "auths": auths, "authsType": authsType })
        
        return HttpResponse(template.render(context))
        #return HttpResponse('ok')
    except Exception, e:
        Log("RoleSetting Error:%s"%e)
        return HttpResponse(e)


@csrf_exempt
def AuthoritySettingOperation(request):
    Log("AuthoritySettingOperation")
    try:
        params = request.GET
        if params.has_key('update'):
            id = params["ID"]
            Log("Update Authority id:" + id) 
            s = Authority.objects.get(ID = id)
            if s is not None:
                s.Name =  params["Name"]
                s.Description = params["Description"]
                s.Type = params["Type"]
                s.save()
                Log("Change PostID:%s " % id)
            else:
                Log("Has not PostID:%s " % id)
        elif params.has_key('add'):
            Log("Add Authority ")  
            c = Authority(Name = params["Name"], Description = params["Description"], Type = params["Type"])
            c.save()
        else:
            id = params["ID"]
            Log("Delete Authority id:" + id) 
            s = Authority.objects.get(ID = id)
            s.delete()
        updateVar("Authority")
        return HttpResponse('ok')
    except Exception, e:
        Log("AuthoritySettingOperation Error:%s"%e)
        return HttpResponse(e)
    
    
@csrf_exempt
def UserSNSInfo(request):
    Log("UserSNSInfo")
    wxAppId = "wx92a26ba6653d5b56" 
    try:
        params = request.GET
        publicAppID = ''
        if params.has_key('code'):
            code = params["code"]
            Log("UserSNSInfo %s"%code, "local", "0.0.0.0", "DEBUG")
            appid = wxAppId  
            publicAppID = params["state"] #用户appid，需要做关联
            (accesstoken,openId) = GetWebAccessToken(code)
            userInfo = GetUserInfo(accesstoken,openId)
            user = wxUserClass(appid,openId)
            user.SetUserInfoWithPublicAppID(json.loads(userInfo),publicAppID)
        url = "/"
        if publicAppID != '':
            url = "/?appid=%s" % publicAppID
        return HttpResponseRedirect(url)
    except Exception, e:
        Log("UserSNSInfo Error:%s"%e)
        return HttpResponse(e)
    
@csrf_exempt
def UserLogin(request):
    Log("UserLogin")
    wxAppId = "wx92a26ba6653d5b56" 
    try:
        params = request.GET
        publicAppID = ''
        url = '/'
        if params.has_key('code'):
            code = params["code"]
            Log("UserLogin %s"%code)
            appid = wxAppId
            #Log("UserLogin 1", "local", "0.0.0.0", "DEBUG")
            (accesstoken,openId) = GetWebAccessToken(code)
            #Log("UserLogin 2", "local", "0.0.0.0", "DEBUG")
            #user = wxUserClass(appid,openId)
            #Log("UserLogin 3", "local", "0.0.0.0", "DEBUG")
            #publicAppID = user.PublicAppID
            publicAppID = wxUser.objects.filter(openID = openId)[0].PublicAppID
        if publicAppID is not None and publicAppID != '':
            url = "/?appid=%s" % publicAppID
        return HttpResponseRedirect(url)
    except Exception, e:
        Log("UserLogin Error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)


def PaidArticleList(request):
    try:
        params = request.GET
        if params.has_key('openid'):
            articles = GetPaidProductsWithWithdraw('',params['openid'])
        else:
            if params.has_key('id'):
                articles = GetPaidProductsWithWithdraw(params['id'])
            else:
                articles = GetPaidProductsWithWithdraw()
        template = loader.get_template('PaidArticles.html')
        context = RequestContext(request, { "articles": articles})       
        return HttpResponse(template.render(context))
    except Exception, e:
        Log("PaidArticleList Error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def CreatePayUrl(request):
    Log("CreatePayUrl")
    url = ''
    try:
        params = request.GET
        if params.has_key('author'):
            name = params['name']
            author = params['author']
            openid = ''
            if params.has_key('openid'):
                openid = params['openid']
                url = GetPayUrl(openid)
            if (url == '' and params.has_key('isNew')):
                ID = int(time.time())
                url = 'pages/pay/index?id=%s&productType=article'%ID
                p = Products(ProductCode = ID, PayUrl=url, OwnerName=author,ProductName=name, ProductType='article',OwnerOpenID = openid)
                p.save()
                updateVar("Products")        
            return HttpResponse(url)
        else:
            template = loader.get_template('CreatePayUrl.html')
            context = RequestContext(request)       
            return HttpResponse(template.render(context))
    except Exception, e:
        Log("CreatePayUrl Error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

    
def wechartWithdraw(request):
    appid = "wx0c0e0edd8eaad932"
    mchid = "1415334402"
    try:
        if request.method == "POST": 
            params = request.POST
        elif request.method == "GET":
            params = request.GET
        
        openid = params['openid']
        res = EnterprisePay(appid, params["amount"], openid, mchid, params["productCode"],params["productType"])

        return HttpResponse(res)
    except Exception, e:
        Log("wechartWithdraw error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('other error:%s'%e)
    
def setWechartPartner(request):
    if request.method == "POST": 
        params = request.POST
        fromUser = params['fromUser']
        toUser = params['toUser']
        Log("setWechartPartner to:%s from:%s"% (toUser,fromUser), "local", "0.0.0.0", "DEBUG")
        mc.set("%s_partner"% fromUser, toUser)
        return HttpResponse('ok')
    elif request.method == "GET":
        params = request.GET
        Log("setWechartPartner %s"% params, "local", "0.0.0.0", "DEBUG")
        #fromUser = params['fromUser']
        #toUser = params['toUser']
        #Log("setWechartPartner to:%s from:%s"% (toUser,fromUser), "local", "0.0.0.0", "DEBUG")
        return HttpResponse('post the paramete')
    return HttpResponse('end')
        
def wxLogin(request):
    try:
        wxAppId = "wx1947bc93e4b75a57"  #生菜阅读服务号
        wxObj = wxAccountInterface.wxAccountInterface(wxAppId)
        url = "http://1.dzhidian.applinzi.com%s" % request.get_full_path()
        ticket = wxObj.GetTicket("jsapi")  
        signature = wxSign(ticket, url).sign()
        template = loader.get_template('wxLogin.html')
        context = RequestContext(request)       
        return HttpResponse(template.render(context))
    except Exception,e:
        Log("wxLogin error:%s"%e, "local", "0.0.0.0", "DEBUG")
        
def GetThirdPartyLessons(request):
    third_party_lessons = getVar('LessonsOfThirdParty').order_by("ChannelID", "Name")
    res = []
    channelDic = GetChannelRemarkDic()
    for lesson in third_party_lessons:
        channel_name = channelDic[lesson.ChannelID]
        name = lesson.Name
        if lesson.SKUName:
            name = "%s %s" % (lesson.Name, lesson.SKUName) 
        res.append({'ID':lesson.ID, "ChannelName": channel_name, "Name": name })
    return HttpResponse(json.dumps(res))
    
    
def UpdateLessonRelation(request):
    try:
        templates = LessonTemplate.objects.all()
        youzan_channel = getVar('Channel').filter(Name='youzan')[0]
        xiaoe_channel = getVar('Channel').filter(Name='xiaoe')[0]
        for template in templates:
            has_lesson = Lesson.objects.filter(Code=template.DazhiCode, TeachingPlan=template.TeachingPlan)
            if len(has_lesson) == 0:
                l = Lesson(Name=template.DazhiName, Code=template.DazhiCode, TeachingPlan=template.TeachingPlan)
                l.save()
                l2 = LessonsOfThirdParty.objects.filter(Name=template.DazhiName,SKUName=template.TeachingPlan, ChannelID=1)
                if not l2:
                    l2 = LessonsOfThirdParty(Name=template.DazhiName,SKUName=template.TeachingPlan, ChannelID=1, TelMsgTemplateID=0)
                    l2.save()
            if template.YouzanName is not None:
                youzan_lesson = LessonsOfThirdParty.objects.filter(Name=template.YouzanName, SKUName=template.YouzanSKU, ChannelID=youzan_channel.ID)
                if len(youzan_lesson) == 0:
                    y = LessonsOfThirdParty(Name=template.YouzanName, SKUName=template.YouzanSKU, ChannelID=youzan_channel.ID)
                    y.save()
                lesson = Lesson.objects.filter(Code=template.DazhiCode, TeachingPlan=template.TeachingPlan)
                youzan_lesson = LessonsOfThirdParty.objects.filter(Name=template.YouzanName, SKUName=template.YouzanSKU, ChannelID=youzan_channel.ID)
                relation = LessonsRelation.objects.filter(LessonID = lesson[0].ID, ThirdPartyID = youzan_lesson[0].ID)
                if len(relation) == 0:
                    r = LessonsRelation(LessonID = lesson[0].ID, ThirdPartyID = youzan_lesson[0].ID)
                    r.save()
            if template.XiaoeName is not None:
                xiaoe_lesson = LessonsOfThirdParty.objects.filter(Name=template.XiaoeName, ChannelID=xiaoe_channel.ID)
                if len(xiaoe_lesson) == 0:
                    x = LessonsOfThirdParty(Name=template.XiaoeName, ChannelID=xiaoe_channel.ID)
                    x.save()
                lesson = Lesson.objects.filter(Code=template.DazhiCode, TeachingPlan=template.TeachingPlan)
                xiaoe_lesson = LessonsOfThirdParty.objects.filter(Name=template.XiaoeName, ChannelID=xiaoe_channel.ID)
                relation = LessonsRelation.objects.filter(LessonID = lesson[0].ID, ThirdPartyID = xiaoe_lesson[0].ID)
                if len(relation) == 0:
                    r = LessonsRelation(LessonID = lesson[0].ID, ThirdPartyID = xiaoe_lesson[0].ID)
                    r.save()
        return HttpResponse('ok')
    except Exception, e:
        Log("UpdateLessonRelation error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)


    
def SignupTemplateMseeage(request):
    params = request.GET
    templateid =  params['template_id']
    unionid = params['unionid']
    appid="wx457b9d0e6f93d1c5"
    wxObj = wxAccountInterface.wxAccountInterface(appid)
    
    wx_user = wxUser.objects.filter(unionID = unionid)
    nickname = ''
    if wx_user:
        nickname = wx_user[0].Name
    res = wxObj.CallTemplateMessage(int(templateid), wx_user[0].openID, nickname, "【小学生中文读写提升必备7堂课】", wx_user[0].Mobile or "您绑定的手机号")
    
    return HttpResponse('发送成功')

def LandingPage(request):
    template = loader.get_template('landing.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def LandingPage2(request):
    template = loader.get_template('landing2.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def LandingMobilePage(request):
    template = loader.get_template('landing_mobile.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def Landing_tempPage(request):
    template = loader.get_template('landing_jpg.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

#大指微信登陆
def wxLoginRedirect(request):
    try:
        admins = ['ob3OJ1ty-6Og_D8j_JXe6fEub0MU','ob3OJ1gIbfmEmP9mMyffhoisb1BQ','ob3OJ1qOVPRpw0d9A23yZ_VrZPTM','ob3OJ1oCsTWazjt_eGcP8A2CoFUk','ob3OJ1oqu6kBUTLCxAlqXXebbZFw','ob3OJ1qK2hsZ7Xs-y6BnuxoQhXvw',
                  'ob3OJ1g2XlwWcdv4mZVHAkbz0YqY','ob3OJ1pmgqzBE7VgiMq-yy_dsOvo','ob3OJ1tp-K2rfUFL0SH6nkrr1E6k','ob3OJ1gsyBNPsK9LnS_9MOBVHjLk','ob3OJ1qHDyTLUtUqyid3hKPEGnzc','ob3OJ1nRMkCNMaNe2JApbb7HUSzI',
                 'ob3OJ1jipvCDgg28aL5vQUqK1pV0','ob3OJ1pK2ao6LyV_CE5NGhD9Fyrk','ob3OJ1kxyMwqDXW2NVO89eIUrMBs','ob3OJ1j7yqJ9SBYXqYGicEneNxvI','ob3OJ1nxx9WZgRD-8fFb45dp3siw','ob3OJ1uX56GcKVKarXCTrJdEUMM0']
        appid = "wx09d63c5dd8a6960d"
        secret = "d86953ed8f623a038039702fd56cfc30"
        params = request.GET
        code = params['code']
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (appid, secret, code)
        res = urllib2.urlopen(url)
        content = json.loads(res.read())
        template = loader.get_template('index.html')
        unionid = content['unionid']
        if unionid in admins:
            context = RequestContext(request, {"Info":("ticket"), "unionid": content['unionid']})
            return HttpResponse(template.render(context)) 
        else:
            Log("wxLoginRedirect failed res:%s"%content, "local", "0.0.0.0", "DEBUG")
            return HttpResponse('登陆失败')
    except Exception,e:
        Log("wxLoginRedirect error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('登陆失败')
    

    
    
def DailyTemplates(request):
    appid="wx457b9d0e6f93d1c5"
    wxObj = wxAccountInterface.wxAccountInterface(appid)
    res = wxObj.SendDailyTemplates()
    return HttpResponse(res)




def setThirdPartyLessonID(request):
    try:
        #names = []
        #newnames = YouzanTrade.objects.values("YouzanName").distinct()
        #for newname in newnames:
        #    third_party = LessonsOfThirdParty.objects.filter(Name=newname['YouzanName'], ChannelID=2)
        #    if not third_party:
        #        names.append(newname['YouzanName'])
        #        l = LessonsOfThirdParty(Name=newname['YouzanName'],SKUName='',ChannelID=2,TelMsgTemplateID=0)
        #        l.save()
        #trades = TradeInfo.objects.filter(ID__lt=27000, ThirdPartyID=None).order_by("-ID")
        #for trade in trades:
        #    youzanName = YouzanTrade.objects.filter(OldName=trade.Name)
        #    if youzanName:
        #        third_party =  LessonsOfThirdParty.objects.filter(Name=youzanName[0].NewName, ChannelID=2)
        #        if third_party:
        #            trade.ThirdPartyID = third_party[0].ID
        #            trade.save()
        return HttpResponse('ok')
    except Exception, e:
        Log("setThirdPartyLessonID error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
        
    
def FunctionTest(request):
    import import_views
    try:
        #updateVar('AllWxAcounts')
        appid = "wx457b9d0e6f93d1c5"
        wxObj = wxAccountInterface.wxAccountInterface(appid)
        #res = coupon_views.GetUserCoupons('13916159092')
        #res = wxObj.SendPointOvertimeRemindTemplate('朱慧',50,30,'oxHGE1N8tF2XLeNKWIoS8a8Zcwao')
        #users = User.objects.filter(ID__lt=2408).order_by("-ID")
        #for user in users:
        #    user_trade = TradeInfo.objects.filter(UserID=user.ID).order_by("PayTime")
        #    if user_trade:
        #        user.Created = user_trade[0].PayTime
        #        user.save()
        
        #updateVar('TelMsgTemplate')
        #day = datetime.now().isoweekday()
        #updateVar('wxMsgTemplate')
        #s = "%s%s%s%s" % ('LN3fF9SkwjM9U23b','1534302535','1199205417','2')
        #md = hashlib.md5(s).hexdigest()

            
            #trade.save()
        #edusoho_lessons = Temp.objects.all()
        #for lesson in edusoho_lessons:
        #    l = LessonsOfThirdParty(Name=lesson.Name, SKUName=lesson.SKUName, ChannelID = 1, TelMsgTemplateID=0)
        #    l.save()
        

        #text = "【外滩教育】您好，感谢您购买外滩教育出品的课程，您的课程已开通，上课网址：外滩云课堂www.ddianke.com，右上角用您的账号和密码登录（账号是您的手机号，初始密码是waitan2016），登陆之后找到“我的学习”，进去之后就能看到您购买的课程了。如果您的手机号已经注册过外滩云课堂，请直接登录。有问题请联系客服WeChat（tbe009），谢谢！"
        #text = "【外滩教育】您的验证码是112233，有效期是10分钟，请尽快输入。"
        #res = Send106txtTelMsg("13916159092", text,1)
        
        #user = User.objects.get(Mobile='13916159092')
        #templates = TelMsgTemplate.objects.filter(ID=1)
        #res = Send106txtTelMsg(user.Mobile,templates[0].Content, 1)
        
        #url="http://47.101.39.80/CreateDzhidianTrade/"
        #res = PostJ(url,{"mobile":"13916159092"})
        #with requests.Session() as s:
        #    res = s.post(url,{"mobile":"13916159092"})
        #req = urllib2.Request(url)
        #res_data = urllib2.urlopen(req)
        #res = res_data.read()

        #res = talk_cloud_interface.GetCompanyFiles()
        #timestamp = GetTimeStamp(datetime.today())
        #third_party_lesson = LessonsOfThirdParty.objects.filter(Name=u"外滩教育 x 罗博深数学系列：小学生数学思维入门课（适合 3-5年级）", SKUName=None, ChannelID=2)
        #updateVar("Lesson")
        #updateVar("LessonsOfThirdParty")
        updateVar("Product")
        updateVar("MiniappProduct")
        #updateVar("LessonCategory")
        #updateVar("ProductAndProductTag")
        #updateVar("ProductTag")
        #updateVar("ProductMessageType")
        #updateVar("MiniappBanner")
        #updateVar("UserPointRate")
        #test_str = 'xxx.aaa.Mp4'
        #strs = test_str.split('.')
        #end_str = strs[len(strs)-1]
        #videos = ['mp4','avi','wmv']
        #res = (end_str.lower() in videos)
        #res = OrderRefund(5)
        #key = 'IGWCHdS58OGbH4OkM1MIL9ZyV6QDQ1hp'
        #m = hashlib.md5()
        #m.update(key.encode('utf8'))
        #key_l = m.hexdigest()
        #text = "Xvh6EqRe1zkmyqvNMaBzhfeF7rHb+Fy/kwVh7neVRuJyRBE+Ot6FE7Ecspp1bzfM4A/1I3UUJRX52WwKAPCTsLofKHFJK84SWY1RigGEVzsNU5IBJbEWtitvLM+r1Mo/f4b5H+X2sYdn4NAzSk2gNmAnjlA9C087TWf4b5v+AqsXX40FAGj8uQ0Z/UlOOhBkqMwsy+vAFwQF/pAxHfO1xQuX2T9Pks03XgfK1tVEiBqOyoptQ4MSv79018lj8MIif2Gfbsf/M5to6Pu35um2+/yCRKZJeHwfG8DapCDB0MJissrXZKG5/CMHQ73/zaUIwo5uj6QdNNqBdzCbWJZg8w9o8B0Mbtzxb8/bb35uoQs6eyaP42NOrsBy0bn+Viogqg4MJCg7cZBsDxnSdBH3byo8ALTTSqnGmzM4F0FH5Dvble8/unyxTA60WHqt4Fa8TG2i+Ua5s/XBe8eTbpz3cgOubUeauLnUu3gmYktty7hBmjy+jVxTG4hfA4+LsZfpjUf3F4T+LJdyPutgXWXOYsqj6afuyHVlfwa984a/6celhM6fHjZHYuMMPp1meXZAi80VbAz7+O96QKlC3DPKwczA5J+P9crM3Npd8VYsgJM3o7dtc8+Rd0AajywQZQz7kWaXmnr5QVH0wEBW8zO89oF+zujA3F4lcKjBYYtHwR5zbUY8nF5OwDYjVWyfswwOHaNIUDbudENzLmy2nEURTU/wIDRZz0OUzfJWkU8TcFirdtbGoaSuytFV9ABxYOLz1oZ/5pa8YfkKifQ1Pg1rgZQb5pqNM9ixQAO2wxJgbO/aX6aSmdhlhdqWj8wi/UfwLXLHjgbCaRwf6kVSihM5i8eI93pbYlh4SewcZGBsgHxKkElDkLQyh/e6nyTfGbv2cejwd+j8Qel4pSuddDih/JHfSDPsQTJTBZ0kiHZPfwVd0Qb7ACUpXBz4QzrNWYR86QF+3wf2s9VRbrmz9bVCDOxU6f4Je5aXelguJ7IXaCJdC+xOju8hptmYsVo8qqpgeYeMu8D1oyOg40Wdq4y1Ig=="
        #text = "Xvh6EqRe1zkmyqvNMaBzhfeF7rHb+Fy/kwVh7neVRuIRR0SBL5ruSZB3KsPFHg2m4A/1I3UUJRX52WwKAPCTsLofKHFJK84SWY1RigGEVzvXjJ6FxmTvVYf3/SUVe6LhT7XW+wa/rbSJE0zfFReMgWAnjlA9C087TWf4b5v+AqsXX40FAGj8uQ0Z/UlOOhBkqMwsy+vAFwQF/pAxHfO1xQuX2T9Pks03XgfK1tVEiBqOyoptQ4MSv79018lj8MIif2Gfbsf/M5to6Pu35um2+/yCRKZJeHwfG8DapCDB0MJissrXZKG5/CMHQ73/zaUIO/gnduSvA9cGp05eiRwwpUS7D1aL3gtW1oRi1ZrxxMB9LJe5RYWs1CXRczcd12P/qg4MJCg7cZBsDxnSdBH3byo8ALTTSqnGmzM4F0FH5Dvble8/unyxTA60WHqt4Fa8TG2i+Ua5s/XBe8eTbpz3cgOubUeauLnUu3gmYktty7hBmjy+jVxTG4hfA4+LsZfpjUf3F4T+LJdyPutgXWXOYsqj6afuyHVlfwa984a/6celhM6fHjZHYuMMPp1meXZAi80VbAz7+O96QKlC3DPKwczA5J+P9crM3Npd8VYsgJM3o7dtc8+Rd0AajywQZQz7kWaXmnr5QVH0wEBW8zO89oF+zujA3F4lcKjBYYtHwR5zbUY8nF5OwDYjVWyfswwOHaNIUDbudENzLmy2nEURTU/wIDRZz0OUzfJWkU8TcFirdtbGoaSuytFV9ABxYOLz1oZ/5pa8YfkKifQ1Pg1rgZQb5pqNM9ixQAO2wxJgbO/aX6aSmdhlhdqWj8wi/UfwUhgebVdW+nteGTQ7pQhms1jOjx4KIqoZwhCbMgrzizFKkElDkLQyh/e6nyTfGbv2cejwd+j8Qel4pSuddDih/JHfSDPsQTJTBZ0kiHZPfwVd0Qb7ACUpXBz4QzrNWYR8sdlGFmn2E6s0XVui04xYRtZ8cvvauonFzniAiv+fWJVdC+xOju8hptmYsVo8qqpgeYeMu8D1oyOg40Wdq4y1Ig=="
        #text = "T87GAHG17TGAHG1TGHAHAHA1Y1CIOA9UGJH1GAHV871HAGAGQYQQPOOJMXNBCXBVNMNMAJAA"
        #text += (16-len(text) % 16) * '='
        #text = base64.b64decode(text)
        #cryptor = AES.new(key_l, AES.MODE_ECB, key_l)

        #Log("FunctionTest 1 %s" % text, "local", "0.0.0.0", "DEBUG")
        #ciphertext = cryptor.decrypt(text)      # 这里就是已经加密了
        #res = AESCipher.AESCipher(key).decrypt(text)
        
        #mc.set("miniapp_access_token_expired",None)
        #res = (datetime.now() - timedelta(days = 365)).strftime("%Y-%m-%d 00:00:00")
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("FunctionTest error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

    
    