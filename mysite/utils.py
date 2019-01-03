#-*- encoding:utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, loader
import pylibmc as memcache
import urllib2
import urllib
import httplib
import hashlib
import cookielib
import json
import base64
import string
import random
import hashlib
from  datetime  import  * 
import time
import struct
import Crypto
from Crypto.Cipher import AES
import xml.etree.cElementTree as ET
import sys
import socket
import ierror
import mimetypes 
import mimetools 
from models import *
from django.db.models import *
import traceback
from Parser import wechatContentParser
import re
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from mem_db_sync import *
import cStringIO
from sae.storage import Bucket
from sae.taskqueue import Task, TaskQueue
from DefClass import *
import requests
import decimal

reload(sys)

sys.setdefaultencoding('utf-8')

mc = memcache.Client()

domain_name = "image"
maxSize = 12097152

DEBUG = False

def Log(strLogInfo, url = "local", ipAddress = "0.0.0.0", Type = "Info"):
    
    s = traceback.extract_stack()
    try:
        if DEBUG or (Type == "DEBUG"):
            oldLog = mc.get("log")
            c = PageLog(URL = url, IPAddress = ipAddress, LogInfo = strLogInfo, TimeStamp = datetime.datetime.now(), Invoker = s[-2][2], LogType = Type)    
            c.save()
        
    except Exception, e:
        oldLog = ""
        oldLog += "\n Time:%s" % datetime.datetime.now()
        oldLog += "\n Invoker:%s" % s[-2][2] 
        oldLog += "\n LogInfo: %s" % strLogInfo
        mc.set("log", oldLog)

    
def ClearLog():
    mc.set("log", "")


def encode_multipart_formdata(fields, files): 
    """ 
    fields is a sequence of (name, value) elements for regular form fields. 
    files is a sequence of (name, filename, value) elements for data to be uploaded as files 
    Return (content_type, body) ready for httplib.HTTP instance 
    """ 
    BOUNDARY = mimetools.choose_boundary() 
    CRLF = '\r\n' 
    L = [] 
    for (key, value) in fields: 
        L.append('--' + BOUNDARY) 
        L.append('Content-Disposition: form-data; name="%s"' % key) 
        L.append('') 
        L.append(value) 
    for (key, filename, value) in files: 
        L.append('--' + BOUNDARY) 
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename)) 
        L.append('Content-Type: %s' % get_content_type(filename)) 
        L.append('') 
        L.append(value) 
    L.append('--' + BOUNDARY + '--') 
    L.append('') 
    body = CRLF.join(L) 
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY 
    return content_type, body 
  
def get_content_type(filename): 
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    
def PostData(url, data):
    
    Log("URL:%s" % url)
    
    try:
        Log("Data:%s" % data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        http_header = {
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
"X-Requested-With" : "XMLHttpRequest",
"Referer" : "http://applinzi.ddianke.com/",
"Accept-Language" : "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
"User-Agent" : "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; Touch; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; InfoPath.3)",
"Host" : "applinzi.ddianke.com",
"DNT" : "1",
"Connection" : "Keep-Alive",
"Cache-Control" : "no-cache"
}        
        req = urllib2.Request(url, data, http_header)
        response = urllib2.urlopen(req)
        Log("Request Method:%s"% req.get_method())
        Log("Response:%s"%response)
        tempDoc = response.read().decode("utf8") 
        return tempDoc
    except Exception, e:
        return "Error when PostData: %s"%e
    
def Post(url, values):
    try:
        data = json.dumps(values,ensure_ascii=False).encode('utf-8')
        Log("Values:%s, IsUnicode:%s" % (data,isinstance(data, unicode) ))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        http_header = {
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
"X-Requested-With" : "XMLHttpRequest",
"Referer" : "http://applinzi.ddianke.com/",
"Accept-Language" : "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
"User-Agent" : "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; Touch; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; InfoPath.3)",
"Host" : "applinzi.ddianke.com",
"DNT" : "1",
"Connection" : "Keep-Alive",
"Cache-Control" : "no-cache"
}        
        req = urllib2.Request(url, data, http_header)
        Log("Request data:%s"% data,Type="DEBUG")
        response = urllib2.urlopen(req)
        #Log("Response:%s"%response,Type="DEBUG")
        tempDoc = response.read().decode("utf8") 
        return tempDoc
    except Exception, e:
        return "Error when Post: %s"%e
    
    
def PostJ(url, values):
    try:
        data = urllib.urlencode(values)
        Log("Values:%s, IsUnicode:%s" % (data,isinstance(data, unicode) ))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        http_header = {
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
"X-Requested-With" : "XMLHttpRequest",
"Referer" : "http://www.ddianke.com/",
"Accept-Language" : "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
"User-Agent" : "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; Touch; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; InfoPath.3)",
"Host" : "www.ddianke.com",
"DNT" : "0",
}        
        req = urllib2.Request(url, data, http_header)
        #Log("Request data:%s"% data,Type="DEBUG")
        response = urllib2.urlopen(req)
        #Log("Response:%s"%response,Type="DEBUG")
        tempDoc = response.read().decode("utf8") 
        return tempDoc
    except Exception, e:
        return "Error when Post: %s"%e
    
    
def PostDataWithCert(url, data):
    
    Log("URL:%s" % url)
    
    try:
        Log("Data:%s" % data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        http_header = {
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
"X-Requested-With" : "XMLHttpRequest",
"Referer" : "http://applinzi.ddianke.com/",
"Accept-Language" : "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
"User-Agent" : "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; Touch; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; InfoPath.3)",
"Host" : "applinzi.ddianke.com",
"DNT" : "1",
"Connection" : "Keep-Alive",
"Cache-Control" : "no-cache"
}        
        CERT_PATH = "/cert/apiclient_cert.pem"
        KEY_PATH = "/cert/apiclient_key.pem"
        req = urllib2.Request(url, data, http_header,cert=(CERT_PATH,KEY_PATH))
        response = urllib2.urlopen(req)
        Log("Request Method:%s"% req.get_method())
        Log("Response:%s"%response)
        tempDoc = response.read().decode("utf8") 
        return tempDoc
    except Exception, e:
        return "Error when PostData: %s"%e
    
def PostFormData(url, data):
    try:
        req=urllib2.Request(url)
        req.add_header('Content-Type', 'multipart/form-data;charset=UTF-8 ')
        req.add_data(data)
        response = urllib2.urlopen(req, timeout=5)
        tempDoc = response.read().decode("utf8") 
        return tempDoc
    except Exception, e:
        return "Error when PostFormData: %s" %e

def PostJson(url,data):
    try:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        http_header = {
            "Content-Type" : "application/json;"
        }        
        req = urllib2.Request(url, json.dumps(data), http_header)
        response = urllib2.urlopen(req)

        return json.loads(response.read().decode("utf8"))
    except Exception, e:
        Log("PostJson failed:%s" % e, Type="DEBUG")
        return None    
    
def LogPV(request):
    
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
        ip =  request.META['HTTP_X_FORWARDED_FOR']  
    else:  
        if request.META.has_key('REMOTE_ADDR'):
            ip = request.META['REMOTE_ADDR']
    Log("PageView", request.get_full_path(), ip, "PageView")

    
def textToDate(text):
    try:
        return time.strptime(text,"%Y%m%d")
    except Exception, e:
        Log("convert failed:%s, text:%s"%(e, text))
        return None


def getArticleSummary(token):
	try:
        
		url = "https://api.weixin.qq.com/datacube/getarticlesummary?access_token=%s" % token
		start = (datetime.datetime.now() - datetime.timedelta(days = 3)).strftime("%Y-%m-%d")
		end = time.strftime("%Y-%m-%d")
		Log("start %s" % start)
		value = { "begin_date": start, "end_date": end}
        #summary = Post(url, value)
		jsonSummary = Post(url, value)
        #Log("jsonSummary: %s" % jsonSummary)
		summary = json.loads(jsonSummary)
		return summary
	except Exception, e:
		Log("Error when getarticlesummary: %s"%e)
        return None

def getBlankDayRecently():
    Log("getBlankDayRecently")
    dateRecently = datetime.datetime.today() + datetime.timedelta(days = 1)
    s = Schedule.objects.filter(ScheduleDate__gt = datetime.date.today()).order_by("ScheduleDate")
    
    if len(s) > 0:
        dateSchedule = s[0].ScheduleDate
        
        if dateRecently.date() >= dateSchedule:
            while dateRecently.date() < s[len(s) - 1].ScheduleDate:
                isSame = 0
                for schedule in s:
                    if dateRecently.date() == schedule.ScheduleDate:
                        isSame = 1
                        dateRecently += datetime.timedelta(days = 1)
                        break
                if isSame == 0:
                    break
        Log(dateRecently.strftime("%Y-%m-%d"))
    return dateRecently

def getAccountConfig(appId):
    Log("getBlankDayRecently appid: %s" % appId)
    defaultConfigs = DefaultConfig.objects.filter(Enable = 1).order_by("ConfigOrder")
    configs = wxConfig.objects.filter(appid = appId)
    for defaultConfig in defaultConfigs:
        for config in configs:
            if config.ConfigName == defaultConfig.ConfigName:
                defaultConfig.ConfigValue = config.ConfigValue
                break
    return defaultConfigs

def GetUserName():
        strNamelist = "徐铮,阎基,平四,胡斐,南兰,汤沛,心砚,马行空,马春花,商宝震,何思豪,田归农,苗人凤,苗若兰,福康安,赵半山,凤南天,袁紫衣,程灵素,姜铁山,陈家洛,李沅芷,余鱼同,宝树,田青文,胡一刀,胡夫人,陶百岁,曹云奇,丁典,狄云,戚芳,血刀老祖,宝象和尚,玄慈,玄寂,玄苦,玄难,玄生,玄痛,阿碧,阿朱,阿紫,段誉,乔峰,梦姑,钟灵,虚竹,谭公,谭婆,谭青,刀白凤,丁春秋,马夫人,巴天石,摘星子,邓百川,风波恶,甘宝宝,公冶乾,木婉清,王语嫣,乌老大,无崖子,云岛主,云中鹤,白世镜,包不同,出尘子,冯阿三,古笃诚,过彦之,平婆婆,石清露,司空玄,司马林,叶二娘,左子穆,华赫艮,李春来,李傀儡,李秋水,刘竹庄,祁六三,全冠清,阮星竹,许卓诚,朱丹臣,波罗星,陈孤雁,何望海,鸠摩智,来福儿,孟师叔,努儿海,宋长老,苏星河,吴长风,吴光胜,吴领军,辛双清,严妈妈,余婆婆,马钰,王罕,冯衡,术赤,华筝,李萍,农夫,曲三,朱聪,杨康,拖雷,郭靖,都史,桑昆,黄蓉,马青雄,小沙弥,木华黎,丘处机,沈青刚,王处一,尹志平,包惜弱,孙不二,札木合,刘玄处,刘瑛姑,吕文德,乔寨主,曲傻姑,全金发,汤祖德,陈玄风,赤老温,陆乘风,陆冠英,沙通天,吴青烈,杨铁心,余兆兴,张阿生,张十五,忽都虎,欧阳峰,欧阳克,者勒米,周伯通,段天德,郭啸天,郝大通,洪七公,侯通海,柯镇恶,南希仁,胖妇人,哑梢公,钱青健,铁木真,盖运聪,黄药师,梁长老,梁子翁,梅超风,博尔忽,博尔术,程瑶迦,韩宝驹,韩小莹,鲁有脚,穆念慈,彭长老,彭连虎,窝阔台,简长老,简管家,裘千仞,裘千丈,察合台,谭处端,一灯大师,,天竺僧人,灵智上人,完颜洪烈,完颜洪熙,焦木和尚,酸儒文人"    
        namelist = strNamelist.split(",")
        index = random.randint(1, len(namelist))
        return namelist[index]

def UploadFileFromUrl(file_name, url, values = None):  
    #url=url+'//' 
    global domain_name
    Log("Upload File From Url")
    try:
        if values is not None:
            data = json.dumps(values,ensure_ascii=False).encode('utf-8')
            req = urllib2.Request(url, data)
            sock=urllib2.urlopen(req)
        else:
            sock=urllib.urlopen(url)
        
        f=sock.read() 
        stream = cStringIO.StringIO(f)
        sock.close()
        bucket = Bucket(domain_name)
        file_name = file_name.replace(' ','')
        bucket.put_object(file_name, stream)
        return_url = bucket.generate_url(file_name)
        Log("Upload File From Url url %s" % return_url)
        return return_url
    except Exception,e:
        Log("Error when Upload File From Url: %s"%e)
    return url

def UploadFile(file_name, file_content): 
    global domain_name, maxSize;
    #Log("UploadFile")
         
    #import sae.const  
    #access_key = sae.const.ACCESS_KEY  
    #secret_key = sae.const.SECRET_KEY  
    #appname = sae.const.APP_NAME  

    try:   
        from sae.storage import Bucket
        bucket = Bucket(domain_name)
        
        file_content.seek(0,2)
        length = file_content.tell()
        if (length > maxSize):
            Log("UploadFile oversize")
            return "oversize"
        else:
            file_name = file_name.replace(' ','')
            file_content.seek(0)
            bucket.put_object(file_name, file_content.read())
            #url = bucket.generate_url(file_name)
            url = "http://applinzi.ddianke.com/%s" % file_name
            Log("UploadFile url %s" % url)
            return url
    except Exception,e:
        Log("Error when UploadFile: %s"%e)
        return None
    file_content.close()
    return None

def random_str(randomLength=8):
    import random,string
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:randomLength])

def random_str2(randomLength=8):
    import random,string
    x = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(x) for i in range(randomLength))

def random_uuid(randomLength=40):
    import random,string
    x = 'abcdef0123456789'
    return ''.join(random.choice(x) for i in range(randomLength))

def random_verificaioncode(randomLength=6):
    import random,string
    x = '123456789'
    return int(''.join(random.choice(x) for i in range(randomLength)))


def GetAllFilesOfStorage():
    global domain_name
    try:   
        
        bucket = Bucket(domain_name)
        fileList = bucket.list()
        L = []
        count = 0;
        for f in fileList:
            #fileTime = f.last_modified.encode()
            #fileTime = fileTime.replace("T", " ").split(".")[0]
            #timeArray = time.strptime(fileTime, "%Y-%m-%d %H:%M:%S")
            #timeStamp = int(time.mktime(timeArray))
            #startTime = "2015-8-2 00:00:00"
            #if timeStamp > time.mktime(time.strptime(startTime,'%Y-%m-%d %H:%M:%S')):
            L.append({"name": f.name, "size": f.bytes, "url": bucket.generate_url(f.name), "last_modified": f.last_modified})
            count = count + 1
        Log("GetAllFilesOfStorage Count %s" % str(count))
        return L
    except Exception,e:
        Log("Error when GetAllFilesOfStorage: %s"%e)
        return None
    return None

def DeleteFileFromStorage(fileName):
    global domain_name
    try:   
        from sae.storage import Bucket
        bucket = Bucket(domain_name)
        bucket.delete_object(fileName);
        Log("DeleteFileFromStorage fileName %s" % fileName)
    except Exception,e:
        Log("Error when DeleteFileFromStorage: %s"%e)
        return None
    return None



def SendTemplateMsg(appid, openid, templateid):
    wxObj = wxAccountInterface.wxAccountInterface(appid)
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % wxObj.GetAccountToken()
    params = {
           "touser":openid,
           "template_id":templateid,
           #"url":"http://weixin.qq.com/download",        
           "data":{
                   "first": {
                       "value":"恭喜你购买成功！",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":"巧克力",
                       "color":"#173177"
                   },
                   "keyword2": {
                       "value":"39.8元",
                       "color":"#173177"
                   },
                   "keyword3": {
                       "value":"2014年9月22日",
                       "color":"#173177"
                   },
                   "remark":{
                       "value":"欢迎再次购买！",
                       "color":"#173177"
                   }
           }
       }
    res = Post(url, params)


def SetNoXLS():
    updateVar("Schedule")
    params ={"callback_url": "http://applinzi.ddianke.com/upload/", 
             "url":"http://www.sina.com"}
    heads = {"Accept": "application/json", 
             "NX-API-KEY": "3d9ce55cca34e37dc454c1467b11bfc6bfaaf746", 
             "no_images": True,
             "disable_smart_width": True}
    try:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        url_values = urllib.urlencode(params)
        url_heads = urllib.urlencode(heads)
        req = urllib2.Request("https://noxls.net/api/v1/convert/html2image", url_values, heads);
        response = urllib2.urlopen(req)
        Log(response.read().decode("utf8"))
    except Exception, e:
        Log( "Error when NoXLS: %s"%e)

        
def GetYouzanToken():
    #token7天过期，提前1小时，以防正好卡在过期时间
    #mc.set("youzan_access_token_expired", datetime.datetime.today())
    if (mc.get("youzan_access_token") is not None and 
        mc.get("youzan_access_token_expired") is not None 
        and mc.get("youzan_access_token_expired") > datetime.datetime.today()):
        Log("youzan_access_token_expired:%s" % mc.get("youzan_access_token_expired"))
    else:
        url = "https://open.youzan.com/oauth/token"
        data = {
            "grant_type":"silent",
            "client_id":"34392ded87a295558b",
            "client_secret":"a711bdffe414a5474fdcb5f643c9fee7",
            "kdt_id":"17328534"
        }
        Log("GetYouzanToken %s"% data['grant_type'], "local", "0.0.0.0", "DEBUG")
        res = PostJson(url, data)
        Log("GetYouzanToken %s"% res, "local", "0.0.0.0", "DEBUG")
        expires_in = res['expires_in'] - 3600
        mc.set("youzan_access_token", res['access_token'])
        mc.set("youzan_access_token_expired", datetime.datetime.today() + datetime.timedelta(seconds=expires_in))
        #res = PostData(url, data)
        Log("GetYouzanToken %s"% res, "local", "0.0.0.0", "DEBUG")
    return mc.get("youzan_access_token")
    
    
def SendSinaTelMsg(mobile,content):
    accesskey='6102'
    secretkey='82d59e1f52ec17758293780a0554d55cb5b5605e'
    url = "http://imlaixin.cn/Api/send/data/json?accesskey=%s&secretkey=%s&mobile=%s&content=%s" % (accesskey,secretkey,mobile,content)                    
    req = urllib2.Request(url)                    
    resp = urllib2.urlopen(req)
    res = json.loads(resp.read())
    Log("SendSinaTelMsg res:%s"%res, "local", "0.0.0.0", "DEBUG")
    nReturn = "1"
    if res['result'] != '01':
        nReturn = res['desc']
    
    return nReturn
    
def Send106txtTelMsg(mobile,content,gwid_type=0):
    #username="929605926"
    #password="CC22C6E7BDDBCD8A88738D811981061F"
    username="k929605926"
    password="E10ADC3949BA59ABBE56E057F20F883E"
    gwid0 = '61'
    gwid='5849e80'
    gwid2='d060613'
    if gwid_type == 1:
        gwid = gwid2
    
    #url="http://api.106txt.com/smsUTF8.aspx?action=Send&username=%s&password=%s&gwid=%s&mobile=%s&message=%s" % (username,password,gwid,mobile,urllib.quote(content))
    #req = urllib2.Request(url)                    
    #resp = urllib2.urlopen(req)
    #res = json.loads(resp.read())
    
    #url="http://api.106txt.com/smsUTF8.aspx?action=Send"
    #url="http://jk.106api.cn/smsUTF8.aspx?type=send"
    url="http://112.126.81.205:533/smsUTF8.aspx?type=send"
    para={
            "username":username,
            "password":password,
            #"gwid":gwid0,
            "gwid":gwid,
            "mobile":mobile,
        	"rece":"json",
            "message":content.encode('utf-8')
        }
    resp = None

    #with requests.Session() as s:
    #    resp = s.post(url,para,headers=http_header)
    #resp = requests.post(url,para,headers=http_header)
    #Log("Send106txtTelMsg resp:%s"%resp.content,Type='DEBUG')
    resp = PostJ(url,para)
    #Log("Send106txtTelMsg resp:%s"%resp,Type='DEBUG')
    res = json.loads(resp)
    #Log("Send106txtTelMsg res:%s"%res,Type="DEBUG")
    AddMessage('text', content, resp, '', mobile)
    #Log("Send106txtTelMsg res:%s"%res)
    nReturn = "1"
    #if res['CODE'] != '1':
    #    nReturn = res['RESULT']
    if res['code'] != '0':
        nReturn = res['remark']
    return nReturn


def GetUserAreaByMobile(mobile):
    try:
        url = 'https://api.it120.cc/common/mobile-segment/location?mobile=%s' % mobile
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        #Log("GetUserAreaByMobile %s" % res, Type="DEBUG")
        if res['code'] == 0:
        
            return res['data']
        else:
            return res['msg']
    except Exception,e:
        Log("GetUserAreaByMobile error %s" % e, Type="DEBUG")
        return e
    

def ImportTradeDetail(tradeID, channelID, isSucceeded, failedType, lessonName, mobile, info, sentInfo = None):
    #Log("ImportInfo start", "local", "0.0.0.0", "DEBUG")
    try:
        c = ImportDetail(TradeID=tradeID, ChannelID=channelID, IsSucceeded=isSucceeded, FailedType= failedType, LessonName=lessonName, Mobile=mobile, Info=info, MsgSentInfo=sentInfo)    
        c.save()
    except Exception, e:
        Log("ImportTradeDetail error:%s"%e, "local", "0.0.0.0", "DEBUG")
        
def GetDecimal(num,digit=2):
    try:
        template = '0.'
        i = 0
        while i < digit:
            template += '0'
            i+=1
        return decimal.Decimal(num).quantize(decimal.Decimal(template))
    except Exception,e:
        return decimal.Decimal(0.0).quantize(decimal.Decimal('0.0'))
        
def GetChannelRemarkDic():
    #updateVar("Channel")
    channels = getVar("Channel")
    dic = {}
    for channel in channels:
        dic[channel.ID] = channel.Remark
    return dic


def GetUserPointRate(code):
    rates = getVar("UserPointRate")
    for rate in rates:
        if rate.Code == code:
            return rate
    return None


def GetCategoryDic():
    #updateVar("Channel")
    categories = getVar("LessonCategory")
    dic = {}
    for category in categories:
        dic[category.ID] = category.Name
    return dic


def GetCategoryNameDic():
        cates = getVar("LessonCategory")
        cateDic = {}
        for cate in cates:
            cateDic[cate.Name] = cate.ID
        return cateDic


def GetCampaignDic():
    #updateVar("Channel")
    campaigns = getVar("Campaign")
    dic = {}
    for campaign in campaigns:
        dic[campaign.ID] = campaign.CName
    return dic



def AddMessage(msg_type, content, result, openid, mobile, msg_info_id=0):
    try:
        message = MessageLog(MsgType=msg_type, Content=content, Result=result, OpenID=openid, Mobile=mobile, MsgInfoID=msg_info_id)
        message.save()
        if msg_info_id:
            message_info = MessageInfo.objects.get(ID = msg_info_id)
            message_info.ReceivedCount += 1
            message_info.save()
    except Exception,e:
        Log("AddMessage error: %s" % e, "local", "0.0.0.0", "DEBUG")
        
        
def GetDateStrByTimeStr(timestr):
    _time = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    return time.strftime("%Y-%m-%d", _time)
        
def GetDateTimeByStr(str_time):
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(str_time,"%Y-%m-%d %H:%M:%S")))

def GetTimeStamp(v_time):
    try:
        #timeArray = time.strptime(v_time, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(v_time.timetuple()))
        return timestamp
    except Exception,e:
        Log("GetTimeStamp error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return 0
    
def GetTimeStampByString(v_time):
    try:
        timeArray = time.strptime(v_time, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timeArray.timetuple()))
        return timestamp
    except Exception,e:
        Log("GetTimeStamp error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return 0
        
def GetDateTimeFromTimeStamp(timestamp):
    try:
        timeArray = time.localtime(timestamp)
        _time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return _time
    except Exception,e:
        Log("GetDateTimeFromTimeStamp error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return None
        
def AESEcrypt(key,text):
        cryptor = AES.new(key, AES.MODE_ECB, key)
        length = 16                    # 这里只是用于下面取余前面别以为是配置
        count = len(text) 
        if (count % length != 0):
            add = length - (count % length)
        else:
            add = 0             #  看看你们对接是满16的时候加上16还是0.这里注意
        text1 = text + ('\0' * add) 

        ciphertext = cryptor.encrypt(text1).encode('hex')       # 这里就是已经加密了
        return ciphertext
        