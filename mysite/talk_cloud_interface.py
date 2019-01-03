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
from django.db.models import Q
from Crypto.Cipher import AES
#import wxAccountInterface

DOMAIN='shwtjy'
AUTH_KEY='LN3fF9SkwjM9U23b'

def CreateClass(name, chairmanpwd, assistantpwd, patrolpwd, confuserpwd, start_time, end_time, room_type=3, video_type=1, video_framerate = 10):
    try:
        start = GetTimeStamp(start_time)
        end = GetTimeStamp(end_time)
        end_time = GetDateTimeFromTimeStamp(end)
        
        url="https://global.talk-cloud.net/WebAPI/roomcreate/key/%s/roomname/%s/roomtype/%d/starttime/%d/endtime/%d/chairmanpwd/%d/assistantpwd/%d/patrolpwd/%d/passwordrequired/1/confuserpwd/%d/videotype/%d/videoframerate/%d/autoopenav/0/" % \
            (AUTH_KEY,name,room_type, start,end,chairmanpwd,assistantpwd,patrolpwd,confuserpwd,video_type,video_framerate)
        Log("CreateClass %s" %url, Type="DEBUG")
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        Log("CreateClass %s" %res, Type="DEBUG")
        
        #url="https://global.talk-cloud.net/WebAPI/entry/domain/%s/serial/%d/username/%s/usertype/2/ts/%s/auth/%d"
        return res
    except Exception,e:
        Log("CreateClass error: %s" %e, Type="DEBUG")
        return None
    
    
def DeleteClassroom(serial):
    try:
        url="http://global.talk-cloud.net/WebAPI/roomdelete/key/%s/serial/%d" % (AUTH_KEY,serial)
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        Log("DeleteClassroom %s" %res, Type="DEBUG")
        return res
    except Exception,e:
        Log("DeleteClassroom error: %s" %e, Type="DEBUG")
        return None
    
    
def GetClassroomURL(serial,name,user_type,current_time,pwd): #user_type:0老师，1:助教，2:学员，3:直播用户，4:巡课
        text ='%s' % pwd
        encrypted = AESEcrypt(AUTH_KEY, text)

        s = "%s%d%d%d" % (AUTH_KEY,current_time,serial,user_type)
        Log("talk_cloud_login_url %s" %s, Type="DEBUG")
        md = hashlib.md5(s).hexdigest()
        url="https://global.talk-cloud.net/WebAPI/entry/domain/%s/serial/%d/username/%s/usertype/%d/ts/%d/auth/%s/userpassword/%s/" % (DOMAIN,serial,name,user_type,current_time,md,encrypted)
        return url
    
    
def GetCompanyFiles():
    try:
        url="https://global.talk-cloud.net/WebAPI/getcompanyfiles/key/%s/" % AUTH_KEY
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        #Log("GetCompanyFiles %s" %res, Type="DEBUG")
        return res
    except Exception,e:
        Log("GetCompanyFiles error: %s" %e, Type="DEBUG")
        return None

    
def UploadWare(upload_file, isopen,dynamicppt, classroom_serial=0):
    try:
        url="https://global.talk-cloud.net/WebAPI/uploadfile/key/%s/isopen/%d/dynamicppt/%d/" % (AUTH_KEY,isopen,dynamicppt) #isdefault/1/
        if classroom_serial:
            url = "%sserial/%d/" % (url, classroom_serial)
        #Log("UploadWare %s" %sys.stdout.encoding, Type="DEBUG")
        file_name = urllib.quote(upload_file.name.encode('utf-8')) #upload_file.name.decode(sys.stdin.encoding).encode('utf-8') #
        #Log("UploadWare %s" %sys.stdin.encoding, Type="DEBUG")
        
        files = {
            "filedata":(file_name,upload_file),
        }
        resp = None
        with requests.Session() as s:
            resp = s.post(url,{"key":AUTH_KEY}, files=files)
        res = json.loads(resp.content)
        Log("UploadWare %s" %res, Type="DEBUG")
        return res
    except Exception,e:
        Log("UploadWare error: %s" %e, Type="DEBUG")
        return None
    
    
def DeleteWare(file_id):
    try:
        url="https://global.talk-cloud.net/WebAPI/deletefile/key/%s/?fileidarr[]=%d" % (AUTH_KEY,file_id) #isdefault/1/
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        Log("DeleteWare %s" %res, Type="DEBUG")
        return res
    except Exception,e:
        Log("DeleteWare error: %s" %e, Type="DEBUG")
        return None
    
    
def ConnectWare(file_id, classroom_serial):
    try:
        url="https://global.talk-cloud.net/WebAPI/roombindfile/key/%s/serial/%d/?fileidarr[]=%d" % (AUTH_KEY,classroom_serial,file_id) #isdefault/1/
        req = urllib2.Request(url)                    
        resp = urllib2.urlopen(req)
        res = json.loads(resp.read())
        Log("ConnectWare %s" %res, Type="DEBUG")
        return res
    except Exception,e:
        Log("ConnectWare error: %s" %e, Type="DEBUG")
        return None
    
    