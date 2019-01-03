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
import wxAccountInterface

        
def TemplatePage(request):
    template = loader.get_template('templateview.html')
    token = time.time()
    context = RequestContext(request, {"Info":("ticket"), "token":token})#{"students":getVar('User')})
    return HttpResponse(template.render(context))

def MsgInfoPage(request):
    template = loader.get_template('messageview.html')
    context = RequestContext(request, {"Info":("ticket")})#{"students":getVar('User')})
    return HttpResponse(template.render(context))   

def TelMessagePage(request):
    template = loader.get_template('telMessagePage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 


def GetTelMsgTemplates(request):
    updateVar("TelMsgTemplate")
    messages = getVar("TelMsgTemplate")
    res = []
    for message in messages:
        edit = "<a href='javascript:edit_msg(%d)'>修改</a>" % (message.ID)
        res.append({"ID":message.ID, "MsgID":message.MsgID, "Content": message.Content, "Edit":edit})
    return HttpResponse(json.dumps(res))

@csrf_exempt
def UpdateTelMsgTemplates(request):
    try:
        params = request.POST
        msg_id = int(params.get('id',0))
        msg_code = int(params.get('code',0))
        msg_content = params.get('content','')
        if not msg_code or not msg_content:
            return HttpResponse('code和内容不能为空')
        if msg_id > 0:
            Log("UpdateTelMsgTemplates msg_id: %d" % msg_id, "local", "0.0.0.0", "DEBUG")
            template = TelMsgTemplate.objects.get(ID=msg_id)
            template.MsgID = msg_code
            template.Content = msg_content
            template.save()
        else:
            template = TelMsgTemplate(MsgID = msg_code, Content = msg_content)
            template.save()
        updateVar("TelMsgTemplate")

        return HttpResponse('ok')
    except Exception,e:
        Log("UpdateTelMsgTemplates error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

    
def TemplateList(request):
    try:
        params = request.GET
        offset=0
        limit=10
        Log("TemplateList params: %s" % params, "local", "0.0.0.0", "DEBUG")
        templates = getVar("wxMsgTemplate")
        
        page = int(offset/limit + 1)
        
        total = len(templates)
        res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        while i < last:
            template = templates[i]
            res.append({"ID":template.ID, 'Name': template.Name, 'First': template.First, "Remark":template.Remark, "Keyword1":template.Keyword1, "Keyword2":template.Keyword2, "Keyword3":template.Keyword3, "Keyword4":template.Keyword4, "Keyword5":template.Keyword5, "Keyword6":template.Keyword6})
            i=i+1
        obj = {
            "page":page,
            "rows":res,
            "total":total
        }
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("TemplateList error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')


def GetAccountTemplates(request):
    try:
        updateVar('AllWxAcounts')
        appid = "wx457b9d0e6f93d1c5"
        wxObj = wxAccountInterface.wxAccountInterface(appid)
        res = wxObj.GetAccountTemplates()
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetAccountTemplates error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def TemplateMsgTask(request):
    try:
        params = json.loads(request.raw_post_data)
        Log("TemplateMsgTask ", Type="DEBUG")
        keys = ['first','remark','keyword1','keyword2','keyword3','keyword4','keyword5','keyword6']
        
        Log("TemplateMsgTask params %s" % params, Type="DEBUG")
        openid = params.get('openid')
        msg_info_id = params.get('msg_info_id')

        Log("TemplateMsgTask openid %s" % openid, Type="DEBUG")
        template_id = params.get('template_id')
        appid = "wx457b9d0e6f93d1c5";
        wxObj = wxAccountInterface.wxAccountInterface(appid)
        paraDic = {}
        paraDic["url"] = params.get('url')
        for key in keys:
            if params.has_key(key):
                paraDic[key] = params[key] #.replace("{username}", user.Name)
        res = wxObj.CallCustomerTemplateMessage(template_id, openid, paraDic, msg_info_id)
        Log("TemplateMsgTask res: %s" % res, Type="DEBUG")
        return HttpResponse(res)
    except Exception, e:
        Log("TemplateMsgTask error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    

@csrf_exempt
def SendTemplateMessage(request):
    try:
        keys = ['first','remark','keyword1','keyword2','keyword3','keyword4','keyword5','keyword6']
        rd_url="http://applinzi.ddianke.com/wxJSWeb/read_count?msg_info_id=%d"
        params = request.POST
        openids = params.get('openids');
        unionid = params.get('unionid')
        token = params.get('token', None)
        
        
        template_id = params.get('template_id')
        #Log("SendTemplateMessage params: %s" % params, "local", "0.0.0.0", "DEBUG")
        appid = "wx457b9d0e6f93d1c5"
        wxObj = wxAccountInterface.wxAccountInterface(appid)
        if unionid:
            openids = []
            user = wxUser.objects.filter(unionID = unionid, SourceAccount=appid)
            if user:
                openids.append(user[0].openID)
        else:
            openids = openids.split(',')
        
        url = params.get('url', None)
        msg_info_id = 0

        #不再需要openid去重
        if token != 'test':
            dic = {}
            for key in keys:
                if params.has_key(key):
                    dic[key] = params[key]
            #(msg_info_id, openids) = GetMessageOpenids(token, openids, json.dumps(dic), url)
            msg_info_id=AddMessageInfo('template',json.dumps(dic), openids, token, url)
        #else:
        #    return HttpResponse('has no token')
        
        paraDic = {}
        if url:
            if msg_info_id:
                paraDic["url"] = rd_url % msg_info_id
            else:
                paraDic["url"] = url
            Log("SendTemplateMessage url: %s" %  paraDic["url"], Type="DEBUG")
        paraDic["msg_info_id"] = msg_info_id
        paraDic["template_id"] = template_id
        
        users = wxUser.objects.values("Name","openID").filter(openID__in = openids)
        queue = TaskQueue('queue_name')
        for user in users:
            for key in keys:
                if params.has_key(key):
                    paraDic[key] = params[key].replace("{username}", user['Name'])
            task_url = "TemplateMsgTask/"
            paraDic["openid"] = user['openID']
            queue.add(Task(task_url, json.dumps(paraDic) ,delay=2))
            #wxObj.CallCustomerTemplateMessage(template_id, user['openID'], paraDic, msg_info_id)
        #UpdateSendResult(msg_info_id)
        #task_url = 'UpdateTemplateSendResult/'
        #queue.add(Task(task_url, json.dumps({"msg_info_id":msg_info_id}) ,delay=2))
        return HttpResponse('ok')
    except Exception, e:
        Log("SendTemplateMessage error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
def GetMessageInfo(request):
    try:
        params = request.GET
        offset=0
        limit=10
        message_infos = MessageInfo.objects.all().order_by("-ID")
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                message_infos = message_infos.filter(Created__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end = datetime.datetime.strptime(end, '%Y-%m-%d') + timedelta(days = 1)
                message_infos = message_infos.filter(Created__lt=end)
            except Exception,e:
                end = None
        Log("GetMessageInfo params: %s" % params, "local", "0.0.0.0", "DEBUG")

        message_infos = message_infos.values("ID","MsgType", "Content", "Targets", "MsgCount", "ReceivedCount", "ReadCount", "Created")
        page = int(offset/limit + 1)
        
        total = len(message_infos)
        res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        while i < last:
            message_info = message_infos[i]
            message_info['ReadPercentage'] = str(GetDecimal(message_info['ReadCount'] * 100.0/message_info['MsgCount']))
            message_info['Created'] = message_info['Created'].strftime("%Y-%m-%d %H:%M:%S")
            message_info['Content'] = json.loads(message_info['Content'])['first']
            res.append(message_info)
            i=i+1
        obj = {
            "page":page,
            "rows":res,
            "total":total
        }
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("GetMessageInfo error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps([]))
        
@csrf_exempt
def UpdateTemplateSendResult(request):
    try:
        params = json.loads(request.raw_post_data)
        Log("UpdateTemplateSendResult params: %s" % params, Type="DEBUG")
        msg_info_id = params.get('msg_info_id')
        UpdateSendResult(msg_info_id)
    except Exception,e:
        Log("UpdateTemplateSendResult error: %s" % e, Type="DEBUG")
    
    
def UpdateSendResult(msg_info_id):
    if msg_info_id:
        message_info = MessageInfo.objects.get(MsgType='template', ID=msg_info_id)
        count = MessageLog.objects.filter(MsgInfoID=msg_info_id, Result__contains="\"ok\"").count()
        Log("UpdateSendResult %d" % count, Type="DEBUG")
        message_info.ReceivedCount = count
        message_info.token = 0
        message_info.save()
        
#用户去重openid的，已经废弃        
def GetMessageOpenids(token, targets, content, url):
    sent_openids = []
    openids = targets
    if token:
        msg_info_id = 0
        message_info = MessageInfo.objects.values("ID").filter(MsgType='template', token=token)
        if message_info:
            message_info = message_info[0]
            msg_info_id = message_info['ID']
            messages = MessageLog.objects.values('OpenID').filter(MsgInfoID=msg_info_id)
            for message in messages:
                sent_openids.append(message['OpenID'])
            openids = [i for i in targets if i not in sent_openids]
        else:
            msg_info_id = AddMessageInfo('template', content, targets, token, url)
    return (msg_info_id, openids)
    
def AddMessageInfo(msg_type, content, targets, token, url):
    try:
        msg_count = len(targets)
        message = MessageInfo(MsgType=msg_type, Content=content, Targets=','.join(targets), MsgCount=msg_count, token=token, rd_url = url)
        message.save()
        return message.ID
    except Exception,e:
        Log("AddMessageInfo error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return 0
        
        
    