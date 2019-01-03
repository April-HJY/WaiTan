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
from django.http import HttpResponseRedirect  
from mem_db_sync import *
from tsaiPlatform import *

@csrf_exempt
def home(request):
    
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
        ip =  request.META['HTTP_X_FORWARDED_FOR']  
    else:  
        if request.META.has_key('REMOTE_ADDR'):
            ip = request.META['REMOTE_ADDR']  
    
    Log("IP Address:%s"%ip)

    if request.method == 'POST':
        #data = json.loads(request.raw_post_data)
        params = request.GET
        if "encrypt_type" in params.keys():
            if (params["encrypt_type"] == "aes"):
                DecrptStr = Decrypt(request.raw_post_data, params["msg_signature"], params["timestamp"], params["nonce"])
                Log("component_verify_ticket Time: %s, Data: %s" % (datetime.now(), DecrptStr),Type="DEBUG" )
                xml = ET.fromstring(DecrptStr)
                try: 
                    InfoType = xml.find("InfoType").text
                    if (InfoType == "component_verify_ticket"):
                        ComponentVerifyTicket = xml.find("ComponentVerifyTicket").text
                        mc.set("ComponentVerifyTicket", ComponentVerifyTicket )
                    else:
                        Log(InfoType)
                        if (InfoType == "unauthorized"):
                            AuthorizerAppid = xml.find("AuthorizerAppid").text
                            wxObj = wxAccountInterface.wxAccountInterface(AuthorizerAppid)
                            wxObj.Unauthorize()
                                #updateVar("AllWxAcounts")

                    
                except Exception,e:
                    Log("Home, Error: %s" % e, Type="DEBUG")
        return  HttpResponse("success")
    
    if request.method == 'GET':
        params = request.GET
        if "auth_code" in params.keys():
            tsaiObj = tsaiPlatform()
            auth_code = params["auth_code"]
            Log("AuthCode:%s"%auth_code)
            wxObj = tsaiObj.GetAuthInfo(auth_code)
            Log("authorizer_appid: %s, Authorizer_access_token:%s"%(wxObj.wxData.appId,wxObj.wxData.AuthCode))
            wxObj.GetAccountInfo()
            updateVar("AllWxAcounts")
            values = {
                      "action": "BuildIndex",
                      "params": wxObj.wxData.appId
                      }
            data = json.dumps(values,ensure_ascii=False).encode('utf-8')
            queue = TaskQueue('queue_name')
            Log("Task Data %s"%data)
            queue.add(Task("action/", data, delay=2))    
        return HttpResponseRedirect("/")
                        
                       
    