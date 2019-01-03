#-*- encoding:utf-8 -*-
from wxUtils import *
import tsaiPlatform 
from mem_db_sync import *

class wxAccountInterface():
    

    def __init__(self,appid):
        self.tsaiObj = tsaiPlatform.tsaiPlatform()
        try:
            self.wxData = wxAccounts.objects.filter(appId = appid)[0]
        except Exception, e:
            self.wxData = wxAccounts(appId = appid)
        
        
    def GetVar(self,strVar):
        if (strVar not in mc):
        #Log("memcache Hit!")
        #return mc.get(strVar)
            self.updateVar(strVar)
        else:
            #Log("Update Var:%s, value: %s" % (strVar,self.getExpireTime(strVar)), Type="DEBUG")
            if self.getExpireTime(strVar)  < datetime.datetime.now():
                #Log("Ticket Expired!", Type="DEBUG")
                self.updateVar(strVar)
    
        return mc.get(strVar)

    def getExpireTime(self,strVar):
        return mc.get("wxTicket_jsapi_expired")
    
    def updateVar(self,strVar):
        expiredTime = "9999-01-01 00:00:00"
        res = ""
        #Log("updateVar:%s"%strVar, Type="DEBUG") 
        if (strVar == 'wxTicket_jsapi'):
            #self.wxData.Expired = datetime.datetime.now()
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=%s" % (self.GetAccountToken(),"jsapi")
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8")
            srcTicket = json.loads(res)  
            res = srcTicket["ticket"]
            expiredTime = datetime.datetime.now() + datetime.timedelta(0, srcTicket["expires_in"] , 0)
        if (strVar == 'wxTicket_wx_card'):
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=%s" % (self.GetAccountToken(),"wx_card")
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            Log(res)
            srcTicket = json.loads(res)  
            res = srcTicket["ticket"]
            expiredTime =  datetime.datetime.now() + datetime.timedelta(0, srcTicket["expires_in"] , 0)
          
        mc.set(strVar, res) 
        mc.set("wxTicket_jsapi_expired",expiredTime )
        return res
        
        
    def GetAccountToken(self): # get the access token of wechat public account
        try:
            if self.wxData.Expired and (self.wxData.Expired > datetime.datetime.now()):
                return self.wxData.AuthCode
            else:
                Log("Token Expired! Start refreshing token with code:%s"%self.wxData.RefreshCode)
                return self.RefreshAccessToken()
        except Exception,e:
            Log("Error in GetAccountToken%s in account: %s"%(e, self.wxData.appName), Type="DEBUG")
            
    

    def UpdateAuthinfo(self,authInfo):
        try:
            if ("authorizer_access_token" in authInfo.keys()):
                authorizer_access_token = authInfo["authorizer_access_token"]
                expires_in = authInfo["expires_in"]
                token_expired = datetime.datetime.now() + datetime.timedelta(0, expires_in , 0)
                Log("authorization_info:%s"%authInfo)
                self.wxData.AuthCode = authorizer_access_token
                self.wxData.Expired = token_expired
            if ("authorizer_refresh_token" in authInfo.keys()):
                self.wxData.RefreshCode = authInfo["authorizer_refresh_token"]
            self.wxData.save()

        except Exception, e:
            Log("Error: %s in UpdateAuthinfo:%s" % (e,authInfo) , Type="Debug") 
        
        
    def RefreshAccessToken(self):
        try:
            
            #component_appid = "wx60072069c7fc883d"
            #appSecret = "0c79e1fa963cd80cc0be99b20a18faeb"
            xx = datetime.datetime.now()
            url = "https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token?component_access_token=%s" % self.tsaiObj.GetAccessToken() 
            values ={
"component_appid":self.tsaiObj.appId,
"authorizer_appid":self.wxData.appId,
"authorizer_refresh_token":self.wxData.RefreshCode,
}
            Log("RefreshAccessToken Started! appid:%s, RefreshCode:%s"%(self.wxData.appId, self.wxData.RefreshCode), Type="DEBUG")
            res = Post(url, values) 
            Log("Result:%s"% res, Type="DEBUG")
            
            access_token = json.loads(res)["authorizer_access_token"]
            expires_in = json.loads(res)["expires_in"]
            authorizer_refresh_token = json.loads(res)["authorizer_refresh_token"]
            expired = datetime.datetime.now() + datetime.timedelta(0, expires_in , 0)
            self.wxData.AuthCode = access_token
            self.wxData.Expired = expired
            self.wxData.RefreshCode = authorizer_refresh_token
            self.wxData.save()
            return access_token
        except Exception,e:
            Log("RefreshAccessToken Error! Msg: %s, appid: %s, RefreshCode: %s"%(e,self.wxData.appId, self.wxData.RefreshCode), Type="DEBUG")
            return None
        
    def GetAccountInfo(self):
        try:
        
            token = self.tsaiObj.GetAccessToken()
            url = "https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info?component_access_token=%s"%token
            values = {
"component_appid": self.tsaiObj.appId ,
"authorizer_appid": self.wxData.appId
}
                  
            Log("GetAccountInfo Started!")
            res = Post(url, values) 
            Log("Result:%s"%res)
            jsonRes = json.loads(res)
            authorizer_info = jsonRes["authorizer_info"]
            nick_name = authorizer_info["nick_name"]
            if "head_img" in authorizer_info.keys():
                head_img = authorizer_info["head_img"]
            else:
                head_img = "" 
            alias = authorizer_info["alias"]
            service_type_info = authorizer_info["service_type_info"]
            user_name = authorizer_info["user_name"]
            qrcode_url = authorizer_info["qrcode_url"]
            authorization_info = jsonRes["authorization_info"]
            
            self.wxData.appName = nick_name
            self.wxData.headImg = head_img
            self.wxData.serviceTypeInfo = service_type_info["id"]
            self.wxData.appUsername = user_name
            self.wxData.QRCodeURL = qrcode_url
            self.wxData.Alias = alias
            self.wxData.Disabled = 0
            self.wxData.OnboardDate = datetime.datetime.now()
            self.wxData.save()
    
        except Exception, e:
            Log("Error when GetAccountInfo - appid:%s, accessToken: %s, Error: %s"%(self.wxData.appId,self.wxData.AuthCode,e))
    
    def GetTicket(self,ticketType):
        
        try:
            return self.GetVar("wxTicket_jsapi") # this is not complete for ticket other than jsapi
        except Exception, e:
            Log("GetTicket Error! %s"%e)
            return ""
        
        
    def GetMediaUrl(self, MEDIA_ID, extension):
        try:
            token = self.GetAccountToken()
            url = "https://api.weixin.qq.com/cgi-bin/material/get_material?access_token=" + token
            Log("GetMediaUrl mediaID: %s" % MEDIA_ID)
            values = {
                "media_id":MEDIA_ID
            }
            res = Post(url, values)
            item = json.loads(res)["news_item"]
            
            thumb_media_id = item[0]["thumb_media_id"]
            values = {
                "media_id":thumb_media_id
            }
            Log("thumb_media_id %s" % thumb_media_id)
            return UploadFileFromUrl(thumb_media_id + extension, url, values)
        except Exception,e:
            Log("Error when GetMediaUrl: %s"%e, Type= "Debug")
        return ""
    
    def RefreshQRCode(self):
        try:
            url = self.wxData.QRCodeURL
            if "mmbiz" in url:
                Log("RefreshQRCode appName %s" % self.wxData.appName)
                newUrl = UploadFileFromUrl(self.wxData.appId + "_QRCode.jpg", url)
                self.wxData.QRCodeURL = newUrl
                self.wxData.save()
            return None
        except Exception,e:
            Log("RefreshQRCode Error!%s"%e, Type = "Debug")
            return None

    def GetNewsCount(self):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/material/get_materialcount?access_token=%s"% self.GetAccountToken()
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            news_count = json.loads(res)["news_count"]
            Log("New Count:%s"%news_count)
            return news_count
        except Exception, e:
            Log("GetNewsAccount Error: %s"%e)
            return 0
    def GetUserCount(self):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s"% self.GetAccountToken()
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            Log(res)
            user_count = json.loads(res)["total"]
            self.wxData.UserCount = user_count
            self.wxData.save()
            Log("User Count:%s"%user_count)
            return user_count
        except Exception, e:
            Log("GetUserCount Error: %s"%e)
            return 0
        
    def GetUserList(self, nextOpenID):
        try:
            if (nextOpenID == "StartOpenID"):
                url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s"% self.GetAccountToken()
            else:
                url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s"% (self.GetAccountToken(),nextOpenID)
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            user_count = json.loads(res)["total"]
            self.wxData.UserCount = user_count
            self.wxData.save()
            Log("User Count:%s"%user_count)
            return json.loads(res)
        except Exception, e:
            Log("GetUserList Error: %s"%e)
            return None
        
    def GetUser(self, openid):
        try:
            accesstoken = self.GetAccountToken()
            url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (accesstoken, openid)
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            #Log("appid: %s, openid: %s" % (self.wxData.appId,openid))
            userInfo = json.loads(res)
            #user = wxUserClass(self.wxData.appId,openid)
            #user.SetUserInfo(userInfo)
            return userInfo
        except Exception, e:
            Log("Error when GetUser: %s" % e)
            return None 
    
    def GetMenuConfig(self):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token=%s" % self.GetAccountToken()
            #url = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s" % 
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            Log(res)
            srcMenu = json.loads(res)
            return srcMenu
        except Exception, e:
            Log("GetMenuConfig Error: %s" % e)
    def GetImageList(self, intFrom, intCount):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=%s" % self.GetAccountToken()
            values = {
    "type":"image",
    "offset":intFrom,
    "count":intCount
}
            res = Post(url, values) 
            #Log("Result:%s"% res)
            resList = json.loads(res)
            item_count = resList["item_count"]
            itemList = resList["item"]
            Log(" Get %s Images:"% item_count)
            return itemList
        except Exception, e:
            Log("GetImageList Error: %s" % e)
            
    def BuildMenu(self):
        try:
            menu = self.GetMenuConfig()
            target = MenuTransform(menu)
            self.CreateMenu(target)
        except Exception, e:
            Log("BuildMenu Error:%s" % e)
            
    def CreateMenu(self, target):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % self.GetAccountToken()
            data = json.dumps(target,ensure_ascii=False)
            target = json.loads(data)
            Log(target)
            #target = {"button": [{"name": "点我点我", "sub_button": [{"media_id": "qSKzF2xLFDdMflbDvfhMdjMnuiLgUl3-OMgSeonIqek", "type": "view_limited", "name": "你好", "sub_button": []}]}, {"media_id": "qSKzF2xLFDdMflbDvfhMdjMnuiLgUl3-OMgSeonIqek", "type": "media_id", "name": "我是图文"}]}
            res = Post(url, target) 
            Log("Result:%s"% res)
        except Exception, e:
            Log("CreateMenu Error:%s" % e)
    def BuildIndex(self, forceUpdate = False):
       
        try:
            #self.BuildAutoReply()
            #UserCount = self.GetUserCount()
            self.RefreshUserList()
            newsCount = self.GetNewsCount()
            
            start = 0
            #lognews = self.GetNewsList(start, newsCount)
            #for newsItem in lognews:
            #    newsmediaID = newsItem["media_id"]
            #    Log("newsmediaID:%s" %newsmediaID)
            if (forceUpdate):
                count = newsCount
            else:
                count = newsCount - self.wxData.ProcessIndex
            Log("BuildIndex started! count: %s" % count)
            while count > 0:
                if count>10:
                    newsToAdd = self.GetNewsList(start, 10)
                    count = count - 10
                    start = start + 10
                else: 
                    newsToAdd = self.GetNewsList(start, count)
                    count = 0
                self.AddNewsList(newsToAdd, forceUpdate)
            updateVar("AllWxAcounts")
            updateVar("wxUserCount")
            updateVar("wxNewsCount")
            updateVar("LatestArticles")
            self.RefreshQRCode()
        except Exception, e:
            Log("BuildIndex Error: %s" %e, Type="DEBUG")
            
    def RefreshUserList(self, forceUpdate = False):
        try:
            nextOpenID = self.wxData.NextOpenID.strip()
            while (nextOpenID != ""):
                return None
                userList = self.GetUserList(nextOpenID)
                Log("UserList: %s" % userList)
                if (userList["count"]>0):
                    for user in userList["data"]["openid"]:
                        self.GetUser(user)
                    self.wxData.NextOpenID = userList["next_openid"]
                    self.wxData.save()
                nextOpenID = userList["next_openid"]
            
        except Exception, e:
            Log("RefreshUserList Error: %s" %e, Type = "DEBUG")
        
        
        
        
    def BuildAutoReply(self):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/get_current_autoreply_info?access_token=%s" % self.GetAccountToken()
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            Log("Getingg AutoReply info: %s" % res)
            autoreply = json.loads(res)     
            if (autoreply['is_add_friend_reply_open'] == 1):
                self.wxData.AutoReply = json.dumps(autoreply["add_friend_autoreply_info"])
                self.wxData.save()
            
        except Exception, e:
            Log("Build AutoReply Error:%s" % e, Type = "Debug")
        
        
        
    def GetNewsList(self, intFrom, intCount):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=%s" % self.GetAccountToken()
            values = {
    "type":"news",
    "offset":intFrom,
    "count":intCount
}
            Log("GetNewsList Started!")
            res = Post(url, values) 
            #Log("Result:%s"% res)
            resList = json.loads(res)
            item_count = resList["item_count"]
            itemList = resList["item"]
            Log(" Read %s News:"% item_count)
            return itemList
        except Exception, e:
            Log("GetNewsList Error: %s" % e, Type= "DEBUG")
            return None
    
    def AddNewsList(self, newsList, forceUpdate = False):
        try:
            for newsItem in newsList:
                UpdateTime = newsItem["update_time"]
                mediaID = newsItem["media_id"]
                for news in newsItem["content"]["news_item"]:
                    self.AddNews(news, UpdateTime, mediaID )
                #Log(" %s News Added!" % len(newsItem["content"]["news_item"]), Type= "DEBUG")
            if (forceUpdate == False):
                self.wxData.ProcessIndex = self.wxData.ProcessIndex + len(newsList)
                self.wxData.save()
            
        except Exception, e:
            Log("AddNewsList Error: %s"%e, Type= "Debug")
            
    def AddNews(self, news, UpdateTime, mediaID, forceUpdate = False):
        try:
            AllArticles = Articles.objects.filter(PostDate = datetime.datetime.fromtimestamp(UpdateTime),  Title = news["title"] )
            
            if (len(AllArticles)==0 ):
                #picURL = "http://mmbiz.qpic.cn/mmbiz/%s/640" % news["thumb_media_id"]
                #Log("AddNews: %s" % news["title"], Type= "DEBUG" )
                
                thumbnail = self.GetMediaUrl(mediaID, ".jpg") #self.GetThumbnail(news["url"])
                c = Articles(PostDate = datetime.datetime.fromtimestamp(UpdateTime), Author = news["author"], Content = news["content"], ArticleURL = news["url"].replace('#rd',''), Title = news["title"], ArticleAbstract = news["digest"], Thumbnail = thumbnail, SourceAccount =  self.wxData.appName, MediaID = mediaID)
                c.save()
                
            else:
                if (forceUpdate):
                    c = AllArticles[0]
                    c.PostDate = datetime.datetime.fromtimestamp(UpdateTime)
                    c.Author = news["author"]
                    c.Content = news["content"]
                    c.ArticleURL = news["url"].rstrip("d").rstrip("r").rstrip("#")
                    c.Title = news["title"]
                    c.ArticleAbstract = news["digest"]
                    c.Thumbnail = self.GetMediaUrl(mediaID) #self.GetThumbnail(news["url"])
                    c.MediaID = mediaID
                    c.save()
                    Log("Force Update!")
                else:
                    Log("Article Found: Title - %s, Author - %s, SourceAccount - %s" % (news["title"], news["author"], self.wxData.appName))
            updateVar("LatestArticles")
        except Exception, e:
            Log("AddNews Error: %s" % e, Type= "Debug")
            
    def GetThumbnail(self, url):
        try:
            response = urllib2.urlopen(url) 
            tempDoc = response.read().decode("utf8") 
            contentParser = wechatContentParser()
            contentParser.feed(contentParser.unescape(tempDoc))
            Log("GetThumbnail:%s"%url)        
            
            if (len(contentParser.strThumbnail)>0):
                return contentParser.strThumbnail
            else:
                return self.wxData.headImg
                    
        except Exception, e:
            Log ("GetThumbnail:%s" % e)        
            return ""
        
        
        
    def AddNewsbyURL(self, url, forceRefresh = False):
        try:
            response = urllib2.urlopen(url) 
            tempDoc = response.read().decode("utf8") 
            contentParser = wechatContentParser()
            contentParser.feed(contentParser.unescape(tempDoc))
            #Info += contentParser.strPostDate + "Author" + contentParser.strAuthor + " strThumbnail: " + contentParser.strThumbnail + "strAbstract" + contentParser.strAbstract + "strTitle:" + contentParser.strTitle +"\n"
            AllArticles = Articles.objects.filter(Title=contentParser.strTitle).filter(Author = contentParser.strAuthor).filter(SourceAccount = self.wxData.appName)
            if (len(AllArticles)==0):
                c = Articles(PostDate = contentParser.strPostDate, Author = contentParser.strAuthor, Content = contentParser.strContent, ArticleURL = url, Title = contentParser.strTitle, ArticleAbstract = contentParser.strAbstract, Thumbnail = contentParser.strThumbnail, SourceAccount = self.wxData.appName)
                c.save()
            else:
                if (forceRefresh):
                    c = AllArticles[0]
                    c.PostDate = contentParser.strPostDate
                    c.Author = contentParser.strAuthor
                    c.Content = contentParser.strContent
                    c.ArticleURL = url
                    c.Title = contentParser.strTitle
                    if (len(contentParser.strThumbnail)>0):
                        c.Thumbnail = contentParser.strThumbnail
                    c.save()
                    Log("forceRefresh News!%s"%c.Title)
                    
                    
        except Exception, e:
            Log ("AddNewsbyURL Error:%s" % e)
    
    def GetConfig(self):
        try:
            resConfig = {
                         'configlist':[]
                         }
            try:
                configlist = json.loads(self.wxData.Config)['configlist']
            except Exception, e:
                configlist = []
            for config in tsaiPlatform.CONFIGURATION_LIST:
                bFound = False
                for item in configlist:
                    if config['configName'] == item['configName']:
                        resConfig['configlist'].append(item)
                        bFound = True
                        break
                if (not bFound):
                    item =  {
                                                 	'configName': config['configName'],
	                                                'configDesc': config['configDesc'],
                                                    'configValue': '0'
                              }
                    resConfig['configlist'].append(item)
            return resConfig
        except Exception, e:
            Log("GetConfig Error: %s, Account: %s" % (e, self.wxData.appName))
            return None
        
        
            
            
    def SaveConfig(self, config):
        try:
            self.wxData.Config = json.dumps(config)
            self.wxData.save()
        except Exception, e:
            Log("SaveConfig Error: %s, Account: %s" % (e, self.wxData.appName))
        
        
    def Unauthorize(self):
        try:
            self.wxData.Disabled = 1
            self.wxData.ProcessIndex = 0
            self.wxData.save()
            updateVar("AllWxAcounts")
        except Exception, e:
            Log("Unauthorize Error：%s" % e)
    
    def GetUserInfo(self, userid):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN " % (self.GetAccountToken(),userid)
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            Log("Getingg User info: %s" % res)
            return res   
            
        except Exception, e:
            Log("GetUserInfo Error: %s" %e)
            
            
    def GetQRCode(self, action_code):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s" % self.GetAccountToken()
            data = {
                "expire_seconds": 604800, 
                "action_name": "QR_STR_SCENE", 
                "action_info": {
                    "scene": {
                        "scene_str": action_code
                    }
                }
            } 
            res = json.loads(Post(url, data))
            ticket = res['ticket']
            url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s" % urllib.quote(ticket)
            response = urllib2.urlopen(url) 
            res = response.read()
            return res
        except Exception, e:
            Log("GetQRCode Error: %s" %e, Type="DEBUG")
            return None
        
    def GetBindingQRCode(self, mini_openid):
        try:
            action_code = "miniopenid_%s" % (mini_openid)
            url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s" % self.GetAccountToken()
            data = {
                "expire_seconds": 604800, 
                "action_name": "QR_STR_SCENE", 
                "action_info": {
                    "scene": {
                        "scene_str": action_code
                    }
                }
            } 
            res = json.loads(Post(url, data))
            ticket = res['ticket']
            url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s" % urllib.quote(ticket)
            response = urllib2.urlopen(url) 
            res = response.read()
            return res
        except Exception, e:
            Log("GetQRCode Error: %s" %e, Type="DEBUG")
            return None
            
    
    def SignupTemplateMseeage(self, params):
        Log("SignupTemplateMseeage2 params: %s" % params, Type="DEBUG")
        openid = params['openid'] 
        redirectUrl = params['redirectUrl']
        first = params['first']
        keyword1 = params['keyword1']
        keyword2 = params['keyword2']
        keyword3 = params['keyword3']
        remark = params['remark']
        #transferTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        template_id = "Wp-jXYNkDNkqIXjDxpfCwBhlv45fhU1PMNew350TEtw"
        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.GetAccountToken()
        
        res = Post(url, params)
        return res
    
    #需要换行处理的标签，数据库出来的unicode不识别换行符
    remarks={
        "1":"登录 http://www.ddianke.com/ ，用户名为您的手机号，初始密码为waitan2016。登陆成功后点击【我的学习】即可观看课程。\n如有任何问题请添加小助手微信: tbe009"
    }
    
    
    def CallTemplateMessage(self, template_id, openid, nickname='', lessonname='', mobile='您绑定的手机号'):
        try:
            template = wxMsgTemplate.objects.get(ID = template_id)
            url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.GetAccountToken()
            remark = str(template.Remark).replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile)
            #if template_id == 1:
            #    remark = self.remarks[str(template_id)].replace("{nickname}", nickname).replace("{lessonname}", lessonname)
            
            params = {
                "touser":openid,
                "template_id":template.TemplateID,
                "url":template.RedirectUrl.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile), 
                "data":{
                    "first": {
                        "value":template.First.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile),
                        "color":"#173177"
                    },
                    "remark":{
                        "value":remark,#.decode("unicode-escape"),#,#str(template.Remark.replace("{nickname}", nickname).replace("{lessonname}", lessonname)),
                        "color":"#173177"
                    }
                }
            }
            if template.KeywordCount >= 1:
                params['data']['keyword1'] = {"value":template.Keyword1.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile), "color":"#173177"}
            if template.KeywordCount >= 2:
                params['data']['keyword2'] = {"value":template.Keyword2.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile), "color":"#173177"}
            if template.KeywordCount >= 3:
                params['data']['keyword3'] = {"value":template.Keyword3.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile), "color":"#173177"}
            if template.KeywordCount >= 4:
                params['data']['keyword4'] = {"value":template.Keyword4.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile), "color":"#173177"}
            if template.KeywordCount >= 5:
                params['data']['keyword5'] = {"value":template.Keyword5.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile), "color":"#173177"}
            if template.KeywordCount >= 6:
                params['data']['keyword6'] = {"value":template.Keyword6.replace("{nickname}", nickname).replace("{lessonname}", lessonname).replace("{mobile}", mobile), "color":"#173177"}
            Log("CallTemplateMessage params: %s" %params)
            res = Post(url, params)
            AddMessage('template', json.dumps(params), res, openid, mobile)
            return json.loads(res)
        except Exception,e:
            Log("CallTemplateMessage error: %s" %e, Type="DEBUG")
            
            
    def CallCustomerTemplateMessage(self, template_id, openid, paramDic, msg_info_id=0):
        try:
            keys = ['first','remark','keyword1','keyword2','keyword3','keyword4','keyword5','keyword6']
            url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.GetAccountToken()
            redirect_url = ''
            redirect_url = paramDic['url']
            first = paramDic['first']
            remark = paramDic['remark']
            params = {
                "touser":openid,
                "template_id":template_id,
                "url":redirect_url,
                "data":{
                    "first": {
                        "value":first,
                        "color":"#173177"
                    },
                    "remark":{
                        "value":remark,
                        "color":"#173177"
                    }
                }
            }
            for key in keys:
                if paramDic.has_key(key):
                    params['data'][key] = {"value":paramDic[key], "color":"#173177"}
            Log("CallCustomerTemplateMessage params: %s" %params)
            res = Post(url, params)
            AddMessage('template', json.dumps(params), res, openid, '', msg_info_id)
            return json.loads(res)
        except Exception,e:
            Log("CallCustomerTemplateMessage error: %s" %e, Type="DEBUG")
            


    def SendDailyTemplates(self):
        try:
            Log("SendDailyTemplates start", "local", "0.0.0.0", "DEBUG")
            #绑定手机送课程的用户
            lesson_id = 92
            #lesson = LessonsOfThirdParty.objects.get(ID = lesson_id)
            trades = TradeInfo.objects.filter(ThirdPartyID = lesson_id)
            user_ids = []
            for trade in trades:
                if trade.UserID in user_ids:
                    continue
                else:
                    user_ids.append(trade.UserID)
                
                user = User.objects.get(ID=trade.UserID)
                wx_user = wxUser.objects.filter(SourceAccount = self.wxData.appId, Mobile = user.Mobile)
                if wx_user:
                    if wx_user[0].VerificationCodeExpired > datetime.datetime.strptime(((datetime.datetime.today() + datetime.timedelta(days = -23)).strftime("%Y-%m-%d") + " 00:00:00"), "%Y-%m-%d %H:%M:%S") and wx_user[0].VerificationCodeExpired < datetime.datetime.strptime(((datetime.datetime.today() + datetime.timedelta(days = -22)).strftime("%Y-%m-%d") + " 00:00:00"), "%Y-%m-%d %H:%M:%S"):
                        self.CallTemplateMessage(2, wx_user[0].openID, wx_user[0].Name, trade.Name, wx_user[0].Mobile or "您绑定的手机号")
                    elif wx_user[0].VerificationCodeExpired > datetime.datetime.strptime(((datetime.datetime.today() + datetime.timedelta(days = -30)).strftime("%Y-%m-%d") + " 00:00:00"), "%Y-%m-%d %H:%M:%S") and wx_user[0].VerificationCodeExpired < datetime.datetime.strptime(((datetime.datetime.today() + datetime.timedelta(days = -29)).strftime("%Y-%m-%d") + " 00:00:00"), "%Y-%m-%d %H:%M:%S"):
                        self.CallTemplateMessage(3, wx_user[0].openID, wx_user[0].Name, trade.Name, wx_user[0].Mobile or "您绑定的手机号")
                    if wx_user[0].VerificationCodeExpired > datetime.datetime.strptime(((datetime.datetime.today() + datetime.timedelta(days = -37)).strftime("%Y-%m-%d") + " 00:00:00"), "%Y-%m-%d %H:%M:%S") and wx_user[0].VerificationCodeExpired < datetime.datetime.strptime(((datetime.datetime.today() + datetime.timedelta(days = -36)).strftime("%Y-%m-%d") + " 00:00:00"), "%Y-%m-%d %H:%M:%S"):
                        self.CallTemplateMessage(4, wx_user[0].openID, wx_user[0].Name, trade.Name, wx_user[0].Mobile or "您绑定的手机号")
            return True
        except Exception,e:
            Log("SendDailyTemplates error:%s"%e, "local", "0.0.0.0", "DEBUG")
            return e
        
        
    def SendClassRemindTemplate(self, name, course_name, start_time, openid):
        try:
            template_id = 'smhKVs_Zv_xwzC2IRcABnx6Wo_QIb707WOnS5Wau-Rk'
            url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.GetAccountToken()
            redirect_url = ''
            first = "%s，您报名的课程即将开始，请您在PC上打开上课网址：class.ddianke.com，请合理安排时间，不要错过。" % name
            remark = "感谢您对外滩的支持与信任，如有疑问，请在学习社群内咨询老师。"
            params = {
                "touser":openid,
                "template_id":template_id,
                "url":redirect_url,
                "data":{
                    "first": {
                        "value":first,
                        "color":"#173177"
                    },
                    "remark":{
                        "value":remark,
                        "color":"#173177"
                    }
                }
            }
            params['data']['keyword1'] = {"value":course_name, "color":"#173177"}
            params['data']['keyword2'] = {"value":start_time, "color":"#173177"}
            Log("SendClassRemindTemplate params: %s" %params)
            res = Post(url, params)
            AddMessage('template', json.dumps(params), res, openid, '', 0)
            return json.loads(res)
        except Exception,e:
            Log("SendClassRemindTemplate error: %s" %e, Type="DEBUG")
            
            
    def SendTeacherClassRemindTemplate(self, name, course_name, start_time, openid):
        try:
            template_id = 'tZBE2h1m9_3dQ9tBgxvg8A3v56GCMV98SBcdZasbzK4'
            url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.GetAccountToken()
            redirect_url = ''
            first = "您好，您负责的课程已排好，请您在PC上打开上课网址：class.ddianke.com，请确认上课时间。"
            remark = "如有变动，请及时联系外滩工作人员，感谢您的支持。"
            params = {
                "touser":openid,
                "template_id":template_id,
                "url":redirect_url,
                "data":{
                    "first": {
                        "value":first,
                        "color":"#173177"
                    },
                    "remark":{
                        "value":remark,
                        "color":"#173177"
                    }
                }
            }
            params['data']['keyword1'] = {"value":course_name, "color":"#173177"}
            params['data']['keyword2'] = {"value":start_time, "color":"#173177"}
            Log("SendClassRemindTemplate params: %s" %params)
            res = Post(url, params)
            AddMessage('template', json.dumps(params), res, openid, '', 0)
            return json.loads(res)
        except Exception,e:
            Log("SendClassRemindTemplate error: %s" %e, Type="DEBUG")
            
            
    def SendPointOvertimeRemindTemplate(self, name, point, days, openid):
        try:
            template_id = '68aF33Fyt7QAZH6SWKjBSbqnyjeG23x4AM7SJaWq7Y4'
            url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.GetAccountToken()
            redirect_url = ''
            first = "%s，您好\r\n您有%d奖学金将于%d天内过期\r\n" % (name, point, days)
            remark = "\r\n外滩教育现推出了系列精品优惠好课，您可以在小程序中查看奖学金情况。奖学金购课可以抵现哦，赶快来看看吧～"
            
            params = {
                "touser":openid,
                "template_id":template_id,
                "miniprogram":{
                 "appid":"wxf11978168e04aba2",
                 "pagepath":"pages/index/index"
               },        
                "data":{
                    "first": {
                        "value":first,
                        "color":"#173177"
                    },
                    "keyword1":{
                        "value":"奖学金",
                        "color":"#173177"
                    },
                    "keyword2":{
                        "value":"%d天以内" % (days),
                        "color":"#173177"
                    },
                    "remark":{
                        "value":remark,
                        "color":"#173177"
                    }
                }
            }
            Log("SendPointOvertimeRemindTemplate params: %s" %params)
            res = Post(url, params)
            AddMessage('template', json.dumps(params), res, openid, '', 0)
            return json.loads(res)
        except Exception,e:
            Log("SendPointOvertimeRemindTemplate error: %s" %e, Type="DEBUG")
            return e
            

    def GetAccountTemplates(self):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token=%s" % self.GetAccountToken()
            response = urllib2.urlopen(url) 
            resp = response.read().decode("utf8") 
            res = json.loads(resp)
            return res
        except Exception,e:
            Log("GetAccountTemplates error:%s"%e, "local", "0.0.0.0", "DEBUG")
            return e
            
            
            
            
            
            
            
            
            
            