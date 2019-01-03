# coding=utf-8
from django.http import HttpResponse
import hashlib, time, re
import xml.etree.ElementTree as ET  
import pylibmc as memcache
import urllib2
from Parser import wechatContentParser
import json
from django.views.decorators.csrf import csrf_exempt  
from django.utils.encoding import *
from models import *
from utils import *
from itertools import *
import threading 
from wxAccountInterface import *
from DefClass import *
#from iQuanwai import *

mc = memcache.Client()

KeywordsFilterList = ["赞", "加油", "晚安", "你好", "好", "好的", "OK", "嗯", "嗯嗯", "恩恩", "哈哈", "呵呵", "hi"]

def implode(list):
    retstr = ""
    for i in list:
        retstr += smart_str(i)
    return retstr


           

class wechatHandler:
    
    def __init__(self, token, xml):
        try:
            #mc.set("log", "Handler initiated started!")
            self.token = token
            self.wxObj = wxAccountInterface(token)
            #self.config = self.GetConfig(self.wxObj.GetConfig())
            self.xml = xml
            self.fromUserName = xml.find("FromUserName").text
            self.toUserName =  xml.find("ToUserName").text
            self.msgType = xml.find ("MsgType").text
            self.user = wxUserClass(token, self.fromUserName)
            if (self.msgType == "image" or self.msgType == "voice"):
                self.mediaId = xml.find("MediaId").text
            #self.InfoType = xml.find("InfoType").text
            #self.ComponentVerifyTicket = xml.find("ComponentVerifyTicket").text    
            userinfo = self.wxObj.GetUser(self.fromUserName)
            #self.user.wxUserData = self.user.SetUserInfo(userinfo)
            self.user.SetUserInfo(userinfo)
            #Log("user ID: %s" % self.user.wxUserData.ID, Type="DEBUG")

            Log("Handler initiated successfully! Token: %s, FromUser:%s, ToUser:%s, msgType: %s"%(token, self.fromUserName, self.toUserName, self.msgType))
        except Exception, e:
            Log( "Couldn't do __init__: %s" % e, Type="DEBUG") 
            
    
    def Execute(self):
        try:
            Log("Entering wechatHandler: execution:%s" % self.msgType)
            #if (self.InfoType == "component_verify_ticket"):
            #    mc.set("ticket", self.ComponentVerifyTicket)
            #    return HttpResponse("success")
            #userInfo = self.wxObj.GetUserInfo(self.fromUserName)
            #Log("UserInfo: %s" % userInfo)
            #user = wxUserClass(json.loads(userInfo))
            operator = {'text':self.HandleText, 'image':self.HandleImage, 'link':self.HandleLink, 'event': self.HandleEvent, 'voice': self.HandleVoice, 'video':self.HandleVoice}
            return operator.get(self.msgType)()
            #return self.HandleText()
        except Exception, e:
            Log("Couldn't do HandleText: %s， msgType:%s" % (e,self.msgType),  Type = "DEBUG")     
       
        
    def GetConfig(self,config):
        try:
            Log("Config processing: %s" % config)
            res = {}
            for item in config['configlist']:
                res[item['configName']] = item['configValue']
            return res    
        except Exception, e:
            Log("GetConfig Error: %s, config: %s" % (e, config ))
            return {}
        
        
        
        
    def HandleText(self):
        try:
            text = smart_str(self.xml.find("Content").text)
            Log( "Entering HandleText:") 
            
            #Test Case
            Log("Enter Test Case Handler...%s"%self.toUserName)
            if (self.toUserName == "gh_3c884a361561"):
                Log("Text:%s"%text, Type="DEBUG")
                if (text.startswith("QUERY_AUTH_CODE")):
                    strQueryCode = text.lstrip("QUERY_AUTH_CODE:")
                    Log("Start Thread...strQueryCode:%s"%strQueryCode, Type="DEBUG")
                    values = {
                      "action": "SendMsg",
                      "params":{
                                "appID": self.token,
                                "toUser":self.fromUserName,
                                "text": strQueryCode
                                }
                      
                      }
                    data = json.dumps(values,ensure_ascii=False).encode('utf-8')
                    queue = TaskQueue('queue_name')
                    Log("Task Data %s"%data, Type="DEBUG")
                    queue.add(Task("action/", data, delay=2))                    
                    return self.ResponseText("")
                return self.ResponseText("TESTCOMPONENT_MSG_TYPE_TEXT_callback")
            #Log("config: %s" % self.config)
            
            res = None
            #res = self.DzhidianHandler(text)

            #先不回消息
            return HttpResponse("")
            #return self.ResponseText("test")

        except Exception, e:
            Log("Couldn't do HandleText: %s" % e, Type="DEBUG") 
            
            
    def DzhidianHandler(self, text):
        try:
            Log("DzhidianHandler text: %s" % text)
            return self.ResponseText("test")
        except Exception,e:
            Log("DzhidianHandler error: %s" % e)
        

    def Search(self,text):
                
            if (len(text)>15 or text in KeywordsFilterList):
                return HttpResponse("")         
            news = []
            date = textToDate(text)
            if (date is not None):
                newsRes = Articles.objects.filter(PostDate=time.strftime("%Y-%m-%d",date)).filter(SourceAccount=self.wxObj.wxData.appName).order_by('-PostDate')
                news = self.SearchResMerge(newsRes,[],[])
                if (len(news)>0):
                    return self.ResponseNews(news[0:7])
            
            AuthorRes = Articles.objects.filter(Author__icontains=text).filter(SourceAccount=self.wxObj.wxData.appName).order_by('-PostDate')
            TitleRes = Articles.objects.filter(Title__icontains=text).filter(SourceAccount=self.wxObj.wxData.appName).order_by('-PostDate')
            ContentRes = Articles.objects.filter(Content__icontains=text).filter(SourceAccount=self.wxObj.wxData.appName).order_by('-PostDate')
            news = self.SearchResMerge(AuthorRes,TitleRes,ContentRes)
             
            #TitleRes = Articles.objects.filter(Title__icontains=text)[0:9]
            if (len(news)==0):
                return self.ResponseText("没有找到结果，请换个关键字试试吧！")
            Log(implode(news)[0:7])
            return self.ResponseNews(news[0:7])
    
    
    def AddNews(self, text):
                Log(text)
                response = urllib2.urlopen(text) 
                Log("URL Openned")
                tempDoc = response.read().decode("utf8") 
                contentParser = wechatContentParser()
                contentParser.feed(contentParser.unescape(tempDoc))
                Log("Parser Ready!")
                #Info += contentParser.strPostDate + "Author" + contentParser.strAuthor + " strThumbnail: " + contentParser.strThumbnail + "strAbstract" + contentParser.strAbstract + "strTitle:" + contentParser.strTitle +"\n"
                AllArticles = Articles.objects.filter(Title=contentParser.strTitle).filter(Author = contentParser.strAuthor).filter(SourceAccount =  self.wxObj.appName)
                    
                if (len(AllArticles)==0):
                    c = Articles(PostDate = contentParser.strPostDate, Author = contentParser.strAuthor, Content = contentParser.strContent, ArticleURL = text, Title = contentParser.strTitle, ArticleAbstract = contentParser.strAbstract, Thumbnail = contentParser.strThumbnail, SourceAccount = self.wxObj.appName)
                    c.save()
                    strComment = "http://applinzi.ddianke.com/articles/?id=%s" % Articles.objects.filter(ArticleURL =  text)[0].ID
                else:
                    strComment = "http://applinzi.ddianke.com/articles/?id=%s" % AllArticles[0].ID
                return self.ResponseText("感谢您的推荐，该链接已加入索引，将会纳入用户搜索范围！访问%s，可开启评论！"% strComment)
    def HandleImage(self):  
        try:                
            userID = mc.get("%s_partner"%  self.user.wxUserData.ID)
            if userID:
                res = wxUser.objects.filter(ID = userID)
                if res:
                    self.SendMsg(res[0], "收到来自用户%s 的图片：  \n <回复消息可在下方直接输入>" % self.user.wxUserData.ID)
                    self.SendImg(res[0].openID, self.mediaId)
                mc.set("%s_partner"% userID, self.user.wxUserData.ID )
                return self.ResponseText("您的图片已经发送给用户:%s" % userID)    

            if (self.config['FaceRecog'] == '1' ):
                return self.FaceRecogHandler()
            return self.ResponseText(self.mediaId)
        except Exception, e:
            Log("Error in HandleImage:%s" %e)
            return self.ResponseText("") 
        
        #headers = {
        ## Basic Authorization Sample
        ## 'Authorization': 'Basic %s' % base64.encodestring('{username}:{password}'),
        #'Content-type': 'application/json',
        #}
        #body = { "url" : url }

        #params = urllib.urlencode({
        # Specify your subscription key
        #'subscription-key': '4fec37522b9247e2ac61fac3143b1301',
    ## Specify values for optional parameters, as needed
    #'analyzesFaceLandmarks': 'true',
    #'analyzesAge': 'true',
    #'analyzesGender': 'true',
    #'analyzesHeadPose': 'true',
    #    })
    def FaceRecogHandler(self):  
        image_url = smart_str(self.xml.find("PicUrl").text)
        api_key = "PtYC2iUyqSy9VoTfGmDSZvSVYriVfvUe" #"35f63a2623cd7955480999e88ee29378"
        api_secret = "Kx7T8vnbNi4gQhd2ROg0ymw5u0JOG_Ce" #"6f30GENbtWQy4EahGFbVswEFAHcpvJnu"
        
        try:
            #url = "http://apicn.faceplusplus.com/v2/detection/detect?api_key=%s&api_secret=%s&url=%s&attribute=glass,pose,gender,age,race,smiling" % (api_key, api_secret, url)
            url = "https://api-cn.faceplusplus.com/facepp/v3/detect"
            postdata = {
                "api_key": api_key,
                "api_secret": api_secret,
                "image_url": image_url,
                "return_attributes": "gender,age,smiling"
                
            }
            params = urllib.urlencode(postdata)  
            
            data = PostData(url, params)
            Log(data)
            
            
            if (len(json.loads(data)["faces"])>0):
                gender = json.loads(data)["faces"][0]['attributes']['gender']['value']
                count = len(json.loads(data)["faces"])
                age = json.loads(data)["faces"][0]['attributes']['age']['value']
                if (gender=="Male"):
                    if (age < 14):
                        gender = "小男孩"
                    else: 
                        if (age > 30):
                            gender = "男士"
                        else:
                            gender = "帅哥"
                        
                    pronoun = "他"
                else:
                    if (age < 14):
                        gender = "小女孩"
                    else:
                        if (age > 30):
                            gender = "女士"
                        else:
                            gender = "美女"
                    pronoun = "她"
                
                Log(gender)
                if (count>1):
                    return self.ResponseText("我找到了%s个人，其中一个是%s，我猜%s拍照时%s岁。"%(count,gender,pronoun,age))
                return self.ResponseText("这是个%s，我猜%s拍照时%s岁。"%(gender,pronoun,age))
            commentstr = """
        pic_media_id = smart_str(self.xml.find("MediaId").text)
        Log("pic_media_id: %s" % pic_media_id)
        media_id_to_show = mc.get("pic_media_id")
        mc.set("pic_media_id", pic_media_id)
        #self.PutVoiceIntoStorage(media_id)
        return self.ResponseImage(media_id_to_show)"""
        except Exception, e:
            Log("[Error: %s"%e)
            #return self.ResponseText("人脸识别功能已暂停，请至http://cn.how-old.net 体验更佳版本！")
        return self.ResponseText("没找到人脸啊:(")
            
        
    
    def HandleLink(self):
        return self.ResponseText("测试")
    
    def HandleVoice(self):
        try:


            userID = mc.get("%s_partner"%  self.user.wxUserData.ID)
            if userID:
                res = wxUser.objects.filter(ID = userID)
                if res:
                    self.SendMsg(res[0], "收到来自用户%s 的语音：  \n <回复消息可在下方直接输入>" % self.user.wxUserData.ID)
                    self.SendVoice(res[0].openID, self.mediaId)
                mc.set("%s_partner"% userID, self.user.wxUserData.ID )
                return self.ResponseText("您的语音已经发送给用户:%s" % userID) 
            ##
            media_id = smart_str(self.xml.find("MediaId").text)
            Log("media_id: %s" % media_id)
            self.PutVoiceIntoStorage(media_id)
            #media_id_to_play = mc.get("media_id")
            #mc.set("media_id", media_id)
            
            #isPlay = mc.get("%s_1" % self.fromUserName)
            
            #if (isPlay is None):
            #    mc.set("%s_1" % self.fromUserName, "played")
            #    self.SendCustomerVoiceMsg("Y0yac6H_wgN7iUH-U7hzBH35mF-YQDvBFnhaJPXTYZE0Y6yPf-OXACY-lGXTxvdR")
            #    Log("media_id_to_play: %s" % media_id_to_play , Type = "DEBUG")
                
            if self.msgType =="voice":
            ##
                openid = self.fromUserName
                sex = self.wxObj.GetUser(openid)["sex"]
                partner = mc.get("%s_partner" % openid)
                Log("Openis:%s, Partner: %s" % (openid, partner))
                boy_list = mc.get("boy_list")
                girl_list = mc.get("girl_list") 
                if not partner:
                    if (sex ==1):
                        if not girl_list:
                            if not boy_list :
                                boy_list=[]
                            if (openid not in boy_list):
                                boy_list.append(openid)
                            mc.set("boy_list", boy_list)
                            mc.set("%s_voice"%openid, media_id)
                            return self.ResponseText("当前没有待匹配的妹子，请稍等哦~")
                        else:
                            partner = girl_list[0]
                            girl_list.remove(partner)
                            mc.set("girl_list", girl_list)
                            mc.set("%s_partner"%openid, partner)
                            mc.set("%s_partner"%partner, openid)
                            voice = mc.get("%s_voice"%partner)
                            self.SendVoice(partner, media_id)
                            self.SendCustomerMsg("恭喜你，匹配成功！现在起发送的语音消息，对方都会收到哦~")
                            
                            return self.ResponseVoice(voice)
                    else:
                        if not boy_list:
                            if not girl_list:
                                girl_list=[]
                            if  (openid not in girl_list): 
                                girl_list.append(openid)
                            mc.set("girl_list", girl_list)
                            mc.set("%s_voice"%openid, media_id)
                            return self.ResponseText("当前没有待匹配的汉子，请稍等哦~")
                        else:
                            partner = boy_list[0]
                            boy_list.remove(partner)
                            mc.set("boy_list", boy_list)
                            mc.set("%s_partner"%openid, partner)
                            mc.set("%s_partner"%partner, openid)
                            voice = mc.get("%s_voice"%partner)
                            self.SendVoice(partner, media_id)
                            self.SendCustomerMsg("恭喜你，匹配成功！现在起发送的语音消息，对方都会收到哦~")
                            return self.ResponseVoice(voice)  
                else:
                    self.SendVoice(partner, media_id)
                    return HttpResponse("")
                      
                        
                return self.ResponseVoice(media_id_to_play)
                Log("media_id_to_play: %s" % media_id_to_play , Type = "DEBUG")
            if self.msgType =="video":
                return self.ResponseVideo(media_id_to_play)
            #return HttpResponse("") 
            
        except Exception, e:
            Log("HandleVoice Error: %s" % e, Type = "DEBUG")
        #return self.ResponseText("你的声音好好听啊，自己输入 接龙 体验一下吧？说不定很快就被人回复了哦")
        
        
    def PutVoiceIntoStorage(self, media_id):
        try:
            #url = "https://api.weixin.qq.com/cgi-bin/material/get_material?access_token=" + self.wxObj.GetAccountToken()
            url = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" % (self.wxObj.GetAccountToken(), media_id)
            values = {
                "media_id":media_id
            }
            
            #sock=urllib.urlopen(url)
            #f=sock.read()
            #url = "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=ACCESS_TOKEN&type=TYPE"
            #    requests.post('http://some.url/streamed', data=f)
            #Log("URL & mediaid: %s, %s"%(url, media_id), Type = "DEBUG" )
            return UploadFileFromUrl(media_id + ".amr", url)
        except Exception, e:
            Log("PutVoiceIntoStorage Error: %s"%e, Type = "DEBUG" )
        return ""
    
    def HandleEvent(self):
        try:
            event = smart_str(self.xml.find("Event").text)
            #Log("HandleEvent: %s" % event, Type="DEBUG")
        #Test Case
        #    if (self.toUserName == "gh_3c884a361561"):
        #        Log("Enter Test Case Handler...%s"%self.toUserName)
        #        return self.ResponseText("%sfrom_callback"%event)
            
                #return self.OnSCANEvent()
            if event == 'subscribe':
                return self.OnSubscribe()
            if event == 'unsubscribe':
                return self.OnUnSubscribe()
            if event == "SCAN":
                return self.OnSCANEvent()
            if event == 'CLICK':
                Log("Click!")
                return self.ResponseText("点击菜单！")
            return HttpResponse("")
        except Exception,e:
            Log("HandleEvent Error: %s, self.xml:%s" % (e,smart_str(self.xml)), Type = "DEBUG")
            
    def SetUserCode(self, code):
                user = wxUser.objects.filter(SourceAccount=self.wxObj.wxData.appId, openID=self.fromUserName)
                if user:
                    user[0].QRCodeTicket = code
                    user[0].save()
                else:
                    userinfo = self.wxObj.GetUser(self.fromUserName)
                    self.user.SetUserInfo(userinfo)
                    self.SetUserCode(code)
                    
    def BindMiniappUser(self, code):
                user = wxUser.objects.filter(SourceAccount=self.wxObj.wxData.appId, openID=self.fromUserName)
                if user:
                    mini_openid = code.replace('miniopenid_','')
                    mini_wxuser = wxUser.objects.filter(openID=mini_openid)
                    if user[0].unionID and mini_wxuser:
                        mini_wxuser[0].unionID = user[0].unionID
                        mini_wxuser[0].save()
                    elif mini_wxuser and mini_wxuser[0].unionID:
                        user[0].unionID = mini_wxuser[0].unionID
                        user[0].save()
                    if mini_wxuser and user[0].MobileBound:
                        mini_wxuser[0].Mobile=user[0].Mobile
                        mini_wxuser[0].save()
                    elif mini_wxuser:
                        user[0].Mobile=mini_wxuser[0].Mobile
                        user[0].MobileBound = 1
                        user[0].save()
                else:
                    userinfo = self.wxObj.GetUser(self.fromUserName)
                    self.user.SetUserInfo(userinfo)
                    self.SetUserCode(code)

    
    def OnSCANEvent(self):
        try:
            code = smart_str(self.xml.find("EventKey").text)
            #Log("OnSCANEvent code: %s" % code, Type="DEBUG")
            #if code == 'None':
            #    return self.ResponseText("")
            if code and code != 'None' and code != 'scan_code':
                code = code.replace('qrscene_','')
                if code.startswith("miniopenid"):
                    self.BindMiniappUser(code)
                    return self.ResponseText("绑定成功")
                else:
                    self.SetUserCode(code);
                    return self.ResponseText("登陆成功")
            else:
                #Log("OnSCANEvent 1", Type="DEBUG")
                msg = "1"
                openid = self.fromUserName
                users = wxUser.objects.filter(openID=openid)
                if users:
                    user = users[0]
                    if not user.MobileBound:
                        msg = """欢迎回到外滩云课堂。

点击下方链接，获取海量好课！https://j.youzan.com/X0sNoY

点击立即领取限时免费课程
http://applinzi.ddianke.com/wxJSWeb/verificationcode"""
                    else:
                        self.wxObj.CallTemplateMessage(6, openid, user.Name, '', user.Mobile or "您绑定的手机号")
                else:
                    msg = """欢迎回到外滩云课堂。

点击下方链接，获取海量好课！https://j.youzan.com/X0sNoY

点击立即领取限时免费课程
http://applinzi.ddianke.com/wxJSWeb/verificationcode"""
                if msg == "1":
                    return HttpResponse("")
                else:
                    return self.ResponseText(msg)
        except Exception,e:
            Log("OnSCANEvent Error: %s" % e, Type = "DEBUG")
            #return self.ResponseText(e)
    
    def OnSubscribe(self):
        try:
            #扫码登陆的不需要发课程模板消息
            code = smart_str(self.xml.find("EventKey").text)
            #Log("OnSCANEvent code: %s" % code, Type="DEBUG")
            if code and code != 'scan_code':
                return self.OnSCANEvent()
            
            openid = self.fromUserName
            #self.wxObj.GetUser(openid)
            #users = wxUser.objects.filter(openID = openid)
            #if users:
            #    user = users[0]
            #    if user.MobileBound:
            #        self.wxObj.CallTemplateMessage(6, openid, user.Name, '', user.Mobile or "您绑定的手机号")

            #return HttpResponse('')
        except Exception, e:
            Log("OnSubscribe Error: %s" % e, Type = "DEBUG")            
            
    def OnUnSubscribe(self):
        try:
            Log("UnSubscribe openid: %s" % self.user.wxUserData.openID, Type="DEBUG")
            self.user.UnSubscribe()
            #user = wxUserClass(token, self.fromUserName)
            #user.UnSubscribe()
            return self.ResponseText("")
        except Exception, e:
            Log("UnSubscribe error: %s" % e, Type = "DEBUG")
    
    #异步消息发送接口#
    def SendVoice(self, openid, media_id):
        values = {
                      "action": "SendVoice",
                      "params":{
                                "appID": self.token,
                                "toUser":openid,
                                "media_id": media_id
                                }
                      
                      }
        data = json.dumps(values,ensure_ascii=False).encode('utf-8')
        queue = TaskQueue('queue_name')
        Log("Task Data %s"%data)
        queue.add(Task("action/", data, delay=2))                    
        return True
    
    def SendImg(self, openid, media_id):
        values = {
                      "action": "SendImage",
                      "params":{
                                "appID": self.token,
                                "toUser":openid,
                                "media_id": media_id
                                }
                      
                      }
        data = json.dumps(values,ensure_ascii=False).encode('utf-8')
        queue = TaskQueue('queue_name')
        Log("Task Data %s"%data)
        queue.add(Task("action/", data, delay=2))                    
        return True
    def SendMsg(self, openid, text):
        
        values = {
                      "action": "SendMsg",
                      "params":{
                                "appID": self.token,
                                "toUser":openid,
                                "text": text
                                }
                      
                      }
        data = json.dumps(values,ensure_ascii=False).encode('utf-8')
        queue = TaskQueue('queue_name')
        Log("Task Data %s"%data)
        queue.add(Task("action/", data, delay=2))                    
        return True        

   
    ## Here are Response functions
    def ResponseText(self,msgText):
        try:
            reply = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                <FuncFlag>0</FuncFlag>
                </xml>"""
            reply = reply % (self.fromUserName, self.toUserName, str(int(time.time())), msgText)
            Log("reply string: %s"%reply)
            retStr = Encrypt(reply, "nonce",  str(int(time.time())))
            Log("Encrypt Str:%s"%retStr)
            return HttpResponse(retStr, content_type="application/xml")
            #return HttpResponse(reply % (self.fromUserName, self.toUserName, str(int(time.time())), msgText), content_type="application/xml")
        except Exception, e:
            Log("Couldn't do ResponseText: %s" % e)         
    
    def ResponseVoice(self, media_id):
        try:
            reply = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[voice]]></MsgType>
<Voice>
<MediaId><![CDATA[%s]]></MediaId>
</Voice>
</xml>"""
            reply = reply % (self.fromUserName, self.toUserName, str(int(time.time())), media_id)
            retStr = Encrypt(reply, "nonce",  str(int(time.time())))
            return HttpResponse(retStr, content_type="application/xml")
        except Exception, e:
            Log("Couldn't do ResponseVoice: %s" % e, Type = "DEBUG")
    
    def SendCustomerMsg(self, text):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % self.wxObj.GetAccountToken()
                
            data = {
    "touser":self.fromUserName,
    "msgtype":"text",
    "text":
    {
      "content":text
    }
}
            res = Post(url, data)
        except Exception, e:
            Log (" Send Customer Msg Error %e" % e, Type ="DEBUG")
        
        
        
    def ResponseVideo(self, media_id):
        try:
            reply = """
            <xml>
            <ToUserName>< ![CDATA[%s] ]></ToUserName>
            <FromUserName>< ![CDATA[%s] ]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType>< ![CDATA[video] ]></MsgType><Video>
            <MediaId>< ![CDATA[%s] ]></MediaId>
            <Title>< ![CDATA[菜园子2018跨年] ]></Title><Description>< ![CDATA[2018我想对菜园子说] ]></Description></Video>
            </xml>
"""
            reply = reply % (self.fromUserName, self.toUserName, str(int(time.time())), media_id)
            retStr = Encrypt(reply, "nonce",  str(int(time.time())))
            return HttpResponse(retStr, content_type="application/xml")
        except Exception, e:
            Log("Couldn't do ResponseVoice: %s" % e, Type = "DEBUG")                
    def ResponseNews(self,news):
        try:
            reply = """<xml>
  			<ToUserName><![CDATA[%s]]></ToUserName>
  			<FromUserName><![CDATA[%s]]></FromUserName>
  			<CreateTime>%s</CreateTime>
  			<MsgType><![CDATA[news]]></MsgType>
  			<ArticleCount>%s</ArticleCount>
  			<Articles>
    		%s
  			</Articles>
  			<FuncFlag>0<FuncFlag>
			</xml>"""
            Log(reply % (self.fromUserName, self.toUserName, str(int(time.time())), len(news), implode(news)))
            return HttpResponse(reply % (self.fromUserName, self.toUserName, str(int(time.time())), len(news), implode(news)), content_type="application/xml")
        except Exception, e:
            Log("Couldn't do ResponseNews: %s" % e)     
      
    def News(self, title, desc, picUrl, linkUrl ):
    	try:
            newsXML = """
    		<item>
  			<Title><![CDATA[%s]]></Title>
  			<Description><![CDATA[%s]]></Description>
  			<PicUrl><![CDATA[%s]]></PicUrl>
  			<Url><![CDATA[%s]]></Url>
			</item>"""
            return newsXML % (title, desc, picUrl, linkUrl)
        except Exception, e:
            Log("Couldn't do News: %s" % e)   
            
    def ResponseImage(self,mediaID):
        try:
            reply = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[%s]]></MediaId>
</Image>
</xml>"""
            reply = reply % (self.fromUserName, self.toUserName, str(int(time.time())), mediaID)
            Log("reply string: %s"%reply)
            retStr = Encrypt(reply, "nonce",  str(int(time.time())))
            Log("Encrypt Str:%s"%retStr)
            return HttpResponse(retStr, content_type="application/xml")
        except Exception, e:
            Log("Couldn't do ResponseImage: %s" % e)                
            

    def SearchResMerge(self,a,b,c):
        news=[]
        for n in a:
            news.append(self.News(n.Title, n.ArticleAbstract, n.Thumbnail, n.ArticleURL))
        if (len(news)<10):  
            for n in b:
                if (n not in a):
                    news.append(self.News(n.Title, n.ArticleAbstract, n.Thumbnail, n.ArticleURL))
                    if (len(news)>=10):
                        break
        if (len(news)<10):    
            for n in c:
                if (n not in (a|b)):
                    news.append(self.News(n.Title, n.ArticleAbstract, n.Thumbnail, n.ArticleURL))
                    if (len(news)>=10):
                        break
        if (len(news)<10):
            return news
        else:
            return news[0:9]

@csrf_exempt
def home(request,token):

    Log(token)
    if request.method == 'GET': 
        #token = "1000000"
        mc.set("log", "This is a start of log:")
        log = mc.get("log")
        params = request.GET
        log += json.dumps(params)
        mc.set("log", log)
        args = [token, params['timestamp'], params['nonce']]
        args.sort()
        if hashlib.sha1("".join(args)).hexdigest() == params['signature']:
            if params.has_key('echostr'):
                return HttpResponse(params['echostr'])
    if request.method == 'POST':
        if request.raw_post_data:
            try:
                params = request.GET
                #return HttpResponse(reply % (toUserName, fromUserName, postTime, "输入点命令吧..."))
                if "encrypt_type" in params.keys():
                    if (params["encrypt_type"] == "aes"):
                        strDecrypt = Decrypt(request.raw_post_data, params["msg_signature"], params["timestamp"], params["nonce"])
                        Log("Decrypt XML Data:%s"%strDecrypt )
                        xml = ET.fromstring(smart_str(strDecrypt))
                    else:
                        xml = ET.fromstring(smart_str(request.raw_post_data))
                else:
                    xml = ET.fromstring(smart_str(request.raw_post_data))    
                
                #xml = "test"
                Log("xml parse successfully!")
                handler = wechatHandler(token, xml)
                return handler.Execute()
            except Exception, e:
                Log("Couldn't do it: %s" % e)  
        return  HttpResponse("Invalid Request!")
