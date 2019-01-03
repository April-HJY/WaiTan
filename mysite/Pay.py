import sys
import traceback
from datetime import *
from models import *
from django.db.models import *
import time
import os
import ssl
from django.http import HttpResponse
from django.template import RequestContext, loader
import httplib
import hashlib
import urllib2
import urllib
import xml.etree.cElementTree as ET
import cStringIO
from sae.storage import Bucket
#import urllib.request

CERTFILE = '../cert/apiclient_cert.pem'
KEYFILE = '../cert/apiclient_key.pem'

def wechartWithdraw(request):
    appid = "wx0c0e0edd8eaad932"
    mchid = "1415334402"
    Log("wechartWithdraw ", "local", "0.0.0.0", "DEBUG")
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

def Log(strLogInfo, url = "local", ipAddress = "0.0.0.0", Type = "Info"):
    c = PageLog(URL = url, IPAddress = ipAddress, LogInfo = strLogInfo, TimeStamp = datetime.datetime.now(), Invoker = 'EnterprisePay', LogType = Type)    
    c.save()

def GetSign(values):
    m = hashlib.md5()
    retStr = ""
    items = values.items()
    items.sort()
    for key,value in items:
        Log("Item:%s"% items)
        retStr += "%s=%s&"%(key, value)
    Log("values:%s"% values)
    strParams = "%skey=dxkugeBP2MvGuFDXdldcehzJzLsciceD" % retStr 
    Log("GetSign for str: %s"%strParams)
    m.update(strParams)
    return m.hexdigest().upper()

def EnterprisePay(appid,amount, openid,mchid, productCode, productType):
    try:
        price = int(amount)
        nonce_str = int(time.time())
        partner_trade_no = nonce_str
        values = {
            "amount": price,
            "check_name": "NO_CHECK",
            "desc": "withdraw",
            "mch_appid":appid,
            "mchid":mchid,
            "nonce_str":nonce_str,
            "openid": openid,
            "partner_trade_no":partner_trade_no,
            "re_user_name": "boss",
            "spbill_create_ip": "167.220.232.147"
        }
        sign =GetSign(values)
        #sign = 'CDATA[DB25A1458276B434E07CB58D00F6DADF'
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
        #url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        
        
        xml = """<xml>
	<mch_appid>%s</mch_appid>
	<mchid>%s</mchid>
	<nonce_str>%s</nonce_str>
    <partner_trade_no>%s</partner_trade_no>
    <openid>%s</openid>
	<check_name>NO_CHECK</check_name>
	<re_user_name>boss</re_user_name>
	<amount>%s</amount>
    <desc>withdraw</desc>
	<spbill_create_ip>167.220.232.147</spbill_create_ip>
	<sign><![CDATA[%s]]></sign>
</xml>"""%(appid, mchid, nonce_str, partner_trade_no, openid,price, sign)
        #%(price, appid, mchid, nonce_str,  openid, partner_trade_no,sign)
        Log("EnterprisePay 1 %s" % xml,"local", "0.0.0.0", "DEBUG")
        
        encodeXML = xml.encode('UTF-8').strip()
  #      encodeXML = """<?xml version="1.0" encoding="utf-8"?><xml>
#	<amount>330</amount>
#	<check_name>FORCE_CHECK</check_name>
#	<desc>withdraw</desc>
#	<mch_appid>wx0c0e0edd8eaad932</mch_appid>
#	<mchid>1415334402</mchid>
#	<nonce_str>1505378461</nonce_str>
#	<openid>oNvgX0WFITP4WESUCPbpUepqOeh0</openid>
#	<partner_trade_no>1505378461</partner_trade_no>
#	<re_user_name>boss</re_user_name>
#	<spbill_create_ip>167.220.232.147</spbill_create_ip>
#	<sign>D23586F08C1BC965099FFDE7BC45C762</sign>
#</xml>""".encode('utf-8').strip()
        certfile = '%s/%s' % (os.path.dirname(__file__),CERTFILE)
        keyfile =  '%s/%s' % (os.path.dirname(__file__),KEYFILE)
        context = ssl.create_default_context(cafile=certfile)
        #context.load_cert_chain(certfile,keyfile)
        #opener = urllib2.build_opener(urllib2.HTTPSHandler(context=context))
                
        Log("EnterprisePay 2 %s" % certfile,"local", "0.0.0.0", "DEBUG")
        #filepath = '%s/%s' % (os.path.dirname(__file__),CERTFILE)
        
        #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        http_header = {
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
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
        #sock = opener.open(url, encodeXML)
        #urllib2.install_opener(opener)
        #req = urllib2.Request(url, encodeXML )
        #response = urllib2.urlopen(req)
        
        #res = response.read()
        #Log("EnterprisePay 2 %s" % res,"local", "0.0.0.0", "DEBUG")
        
        #resURL = UploadFileFromUrl('xxx%s.xml'%nonce_str,url, encodeXML)
        
        #req = urllib2.Request(url, encodeXML)
        sock=urllib2.urlopen(url,encodeXML, cafile=certfile)
        f=sock.read()
        stream = cStringIO.StringIO(f)
        sock.close()
        bucket = Bucket("image")
        bucket.put_object('xxxaaa.xml', stream)
        return_url = bucket.generate_url('xxxaaa.xml')
        
        #Log(return_url,"local", "0.0.0.0", "DEBUG")

        xml = ET.fromstring(res)
        Log(xml,"local", "0.0.0.0", "DEBUG")
        result_code = xml.find("result_code").text
        return_msg = 'SUCCESS'
        Log("EnterprisePay 3","local", "0.0.0.0", "DEBUG")
        if result_code != 'SUCCESS':
            return_msg = xml.find("return_msg").text
            err_code = xml.find("err_code").text
            Log("EnterprisePay err_code:%s" % err_code,"local", "0.0.0.0", "DEBUG")
        else:
            b = BusinessSpending(TradeNo = partner_trade_no, Amount=amount, ProductCode = productCode, ProductType = productType, TargetOpenID = openid)
            b.save()
        Log("EnterprisePay 4","local", "0.0.0.0", "DEBUG")
        return return_msg
    except Exception, e:
        Log("EnterprisePay error:%s" % e,"local", "0.0.0.0", "DEBUG")
        return e
