# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, loader
from telnetlib import *
from django.db import connection,transaction 
from models import *
from Parser import wechatContentParser
import HTMLParser
import os
import urllib2
import time
import pylibmc as memcache
from utils import *
from wxAccountInterface import *

mc = memcache.Client()
def home(request):
	
    #log = mc.get("log")
    if request.method == 'GET': 
        params = request.GET
        url = params['url']
        #log += url
        #mc.set("log", log)
        template = loader.get_template('Homepage.html')
        #url = "http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MjM5MDE0ODM3Mg==#wechat_webview_type=1&wechat_redirect"
        if len(url) >0 :
            response = urllib2.urlopen(url) 
            tempDoc = response.read().decode("utf8") 
            contentParser = wechatContentParser()
            contentParser.feed(contentParser.unescape(tempDoc))
            #Info += contentParser.strPostDate + "Author" + contentParser.strAuthor + " strThumbnail: " + contentParser.strThumbnail + "strAbstract" + contentParser.strAbstract + "strTitle:" + contentParser.strTitle +"\n"
            AllArticles = Articles.objects.filter(Title=contentParser.strTitle).filter(Author = contentParser.strAuthor)
            if (len(AllArticles)==0):
                c = Articles(PostDate = contentParser.strPostDate, Author = contentParser.strAuthor, Content = contentParser.strContent, ArticleURL = url, Title = contentParser.strTitle, ArticleAbstract = contentParser.strAbstract, Thumbnail = contentParser.strThumbnail, SourceAccount = contentParser.strSource)
                c.save()
            
    if request.method == 'POST':
        #postData = json.loads(request.raw_post_data) #全网发布检测需要用此项
        postData = request.POST
        #Log("PostData:%s"%postData, Type="DEBUG")
        try:
            eval(postData["action"])(json.loads(postData["params"]))
            #eval(postData["action"])(postData["params"])#全网发布检测需要此项
        except Exception,e:
            Log("home SendMsg :%s"%e, Type="DEBUG")
    #urllist = url.split("http://")   
    #Info = ""
    #for u in urllist:
    #    response = urllib2.urlopen("http://"+u) 
    #    tempDoc = response.read().decode("utf8") 
    #    contentParser = wechatContentParser()
    #    contentParser.feed(contentParser.unescape(tempDoc))
    #    #Info += contentParser.strPostDate + "Author" + contentParser.strAuthor + " strThumbnail: " + contentParser.strThumbnail + "strAbstract" + contentParser.strAbstract + "strTitle:" + contentParser.strTitle +"\n"
    #    c = Articles(PostDate = contentParser.strPostDate, Author = contentParser.strAuthor, Content = contentParser.strContent, ArticleURL = "http://"+u, Title = contentParser.strTitle, ArticleAbstract = contentParser.strAbstract, Thumbnail = contentParser.strThumbnail)
    #    c.save()
        #break;
    context = RequestContext(request, {"Info":"OK"})
    return HttpResponse("OK")

def BuildIndex(appid):
    wxObj = wxAccountInterface(appid)
    wxObj.BuildIndex()

def SendMsg(params):
    try:
        Log("params:%s"% params, Type="DEBUG")
        strAppID = params["appID"]
        strToUser = params["toUser"]
        text = params["text"]
        Log("SendMsg AppID:%s, toUser:%s, Text:%s"%(strAppID,strToUser,text), Type="DEBUG")
        #authorizer_appid,authorizer_access_token, authorizer_refresh_token = GetAuthInfo(self.strQueryCode)
        #Log("authorizer_appid: %s, Authorizer_access_token:%s"%(authorizer_appid,authorizer_access_token))
        #GetAccountInfo(authorizer_appid, authorizer_access_token)
        
        wxTempObj = wxAccountInterface(strAppID)
        strAccessToken = wxTempObj.GetAccountToken()
        Log("GetAccessToken:%s"%strAccessToken)
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s"%strAccessToken
        values = {
            "touser":strToUser,
            "msgtype":"text",
            "text":
            {
                 "content":text
            }
        }
        Log("Read to send CRM message:%s"%values)
        res = Post(url, values)
    except Exception,e:
        Log("Error in SendMsg:%s"%e, Type="DEBUG")
        
def SendSignupTemplateMseeage(params):
    appid = params["appID"]
    openid = params["openID"]
    className = params["name"]
    signupTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template_id = "cZBmCjkFan3TW9nXpfEYciKJV9pDqCbKPt12BtWb7dc"
    wxObj = wxAccountInterface(appid)
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % wxObj.GetAccountToken()
    params = {
           "touser":openid,
           "template_id":template_id,
           #"url":"https://applinzi.ddianke.com/wxJSWeb/bindusertoken",        
           "data":{
                   "first": {
                       "value":"报名成功！",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":className,
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":signupTime,
                       "color":"#173177"
                   },
                   "remark":{
                       "value":"祝您学习愉快",
                       "color":"#173177"
                   }
                }
            }
    res = Post(url, params)
    return res
        
def SendVoice(params):
    try:
        strAppID = params["appID"]
        strToUser = params["toUser"]
        media_id = params["media_id"]
        Log("AppID:%s, toUser:%s, Text:%s"%(strAppID,strToUser,media_id))
        #authorizer_appid,authorizer_access_token, authorizer_refresh_token = GetAuthInfo(self.strQueryCode)
        #Log("authorizer_appid: %s, Authorizer_access_token:%s"%(authorizer_appid,authorizer_access_token))
        #GetAccountInfo(authorizer_appid, authorizer_access_token)
        
        wxTempObj = wxAccountInterface(strAppID)
        strAccessToken = wxTempObj.GetAccountToken()
        Log("GetAccessToken:%s"%strAccessToken)
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s"%strAccessToken
        values = {
             "touser": strToUser,
             "msgtype":"voice",
             "voice":
            {
            "media_id":media_id
            }
        }
        Log("Read to send CRM message:%s"%values)
        res = Post(url, values)
    except Exception,e:
        Log("Error in SendVoice%s"%e)

def SendImage(params):
    try:
        strAppID = params["appID"]
        strToUser = params["toUser"]
        media_id = params["media_id"]
        Log("AppID:%s, toUser:%s, Text:%s"%(strAppID,strToUser,media_id))
        #authorizer_appid,authorizer_access_token, authorizer_refresh_token = GetAuthInfo(self.strQueryCode)
        #Log("authorizer_appid: %s, Authorizer_access_token:%s"%(authorizer_appid,authorizer_access_token))
        #GetAccountInfo(authorizer_appid, authorizer_access_token)
        
        wxTempObj = wxAccountInterface(strAppID)
        strAccessToken = wxTempObj.GetAccountToken()
        Log("GetAccessToken:%s"%strAccessToken)
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s"%strAccessToken
        values = {
             "touser": strToUser,
             "msgtype":"image",
             "image":
            {
            "media_id":media_id
            }
        }
        Log("Read to send CRM message:%s"%values)
        res = Post(url, values)
    except Exception,e:
        Log("Error in SendVoice%s"%e)
        