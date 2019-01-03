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
import pymysql
from XiaoeSDK import XiaoeSDK
from django.db.models import Q
import wxAccountInterface
import wxUtils
#import requests
#from datetime import *
import point_views

config = {
        'host':'47.98.218.185',
        'port':3306,
        'user':'dzhidian',
        'password':'dzhidian',
        'db':'edusoho',
        'charset':'utf8mb4',
        'cursorclass':pymysql.cursors.DictCursor,
    }


def ImportDetailPage(request):
    #Log("ImportDetailPage start", "local", "0.0.0.0", "DEBUG")
    template = loader.get_template('importdetail.html')
    context = RequestContext(request, {"Info":("ticket")})#{"students":getVar('User')})
    return HttpResponse(template.render(context))

    
def ImportDetailList(request):
    try:
        params = request.GET
        offset=0
        limit=10
        Log("ImportDetailList params: %s" % params, "local", "0.0.0.0", "DEBUG")
        importdetail = ImportDetail.objects.order_by("-TimeStamp") #getVar('ImportDetail')
        channelDic = GetChannelRemarkDic()
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                importdetail = importdetail.filter(TimeStamp__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end = datetime.datetime.strptime(end, '%Y-%m-%d') + timedelta(days = 1)
                importdetail = importdetail.filter(TimeStamp__lt=end)
            except Exception,e:
                end = None
        if params.has_key('failedType'):
            failedType=params['failedType']
            if failedType is not None and failedType != '' and failedType != 'all':
                importdetail = importdetail.filter(FailedType=failedType)
        if params.has_key('channel'):
            channelID=params['channel']
            try:
                if channelID is not None and channelID != '' and channelID != 'all':
                    importdetail = importdetail.filter(ChannelID=int(channelID))
            except Exception, e:
                channelID=None

        page = int(offset/limit + 1)
        
        total = len(importdetail)
        res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        while i < last:
            detail = importdetail[i]
            channelRemark = channelDic[detail.ChannelID]
            res.append({"ID":detail.ID, 'TradeID': detail.TradeID, 'Mobile': detail.Mobile, 'ChannelName':channelRemark, 'IsSucceeded':detail.IsSucceeded, 
                        'FailedType':detail.FailedType, 'Info':detail.Info, 'LessonName':detail.LessonName, 'TimeStamp':detail.TimeStamp.strftime("%Y-%m-%d %H:%M:%S"), 'MsgSentInfo':detail.MsgSentInfo})
            i=i+1
        #Log("StudentList res: %s" % res, "local", "0.0.0.0", "DEBUG")
        obj = {
            "page":page,
            "rows":res,
            "total":total
        }
        
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("ImportDetailList error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')
    
    
def ImportTradeInfo(info,  infoType = "Info"):
    #Log("ImportInfo start", "local", "0.0.0.0", "DEBUG")
    try:
        c = ImportInfo(Info=info, TimeStamp = datetime.datetime.now(), InfoType=infoType)    
        c.save()
    except Exception, e:
        Log("ImportTradeInfo error:%s"%e, "local", "0.0.0.0", "DEBUG")

def UpdateThirdPartyTrades(request):
    try:
        #ImportInfo1("aa","bb")
        #Log("ImportInfo start", "local", "0.0.0.0", "DEBUG")
        Log("UpdateThirdPartyTrades start", "local", "0.0.0.0", "DEBUG")
        updateVar('Channel')
        updateVar("Lesson")
        updateVar("LessonsOfThirdParty")
        updateVar("LessonsRelation")
        updateVar("TelMsgTemplate")
        updateVar("wxMsgTemplate")
        UpdateYouzanTradesByPage()
        UpdateXiaoeTradesByPage()
        Log("UpdateThirdPartyTrades 1", "local", "0.0.0.0", "DEBUG")
        #res = InsertEdusoho()
        res = InsertEdusohoAli()
        return HttpResponse(res)

    except Exception, e:
        Log("UpdateThirdPartyTrades error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    

def InsertEdusoho():
    
    try:
        #users = getVar("User").filter(IsImported = 0)
        trades = TradeInfo.objects.filter(IsImported = 0)
        Log("InsertEdusoho count:%d"%len(trades), "local", "0.0.0.0", "DEBUG")
        admin = None
        mobiles = []
        connection = pymysql.connect(**config)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE nickname = 'admin' LIMIT 1")
                admin = cursor.fetchone()
        except Exception, e:
            #ImportTradeInfo(e, "InsertEdusoho")
            Log("InsertEdusoho error 1:%s"%e, "local", "0.0.0.0", "DEBUG")
        finally:
            connection.close()
        for trade in trades:
            imported = CreateDzhidianTrade(admin, trade)
            if imported != 'error':
                trade.IsImported = True
                trade.save()
        #updateVar("User")
        #updateVar("ImportDetail")
        Log("InsertEdusoho success", "local", "0.0.0.0", "DEBUG")
        return 'ok'
    except Exception, e:
        Log("InsertEdusoho error: %s"%e, "local", "0.0.0.0", "DEBUG")
        return e
        #ImportTradeInfo(e, "InsertEdusoho")
        
        
def InsertEdusohoAli():
    try:
        trades = TradeInfo.objects.filter(IsImported = 0)
        Log("InsertEdusohoAli count:%d"%len(trades), "local", "0.0.0.0", "DEBUG")
            
        for trade in trades:
            CreateDzhidianTradeAli(trade);
            trade.save()
            #break
        #updateVar("ImportDetail")
        Log("InsertEdusohoAli success", "local", "0.0.0.0", "DEBUG")
        return 'ok'
    except Exception, e:
        Log("InsertEdusohoAli error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return e
        
def CreateDzhidianTradeAli(trade):
            user = User.objects.get(ID=trade.UserID)
            third_partys = LessonsOfThirdParty.objects.filter(Name=trade.Name, ChannelID=trade.ChannelID)
            tradeObj = {"TradeID":trade.TradeID,"ChannelID":trade.ChannelID,"Name":trade.Name}
            if third_partys is None or len(third_partys) == 0:
                ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", trade.Name, None, "对应表里没有找到符合的课程名，可能是代理销售课程")
                trade.IsImported = True
                #ImportTradeInfo("InsertTrade error: no lesson match tradeID: %d %s %d" % (trade.ID, trade.Name, trade.ChannelID), "InsertTrade")
                return
            #考虑SKU again
            third_party = None
            for third_party_i in third_partys:
                if third_party_i.SKUName:
                    if third_party_i.SKUName == trade.SKUName:
                        third_party = third_party_i
                else:
                    third_party = third_party_i
            
            #third_party = third_partys[0]
            if not third_party:
                ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", "%s %s" % (trade.Name, trade.SKUName) , None, "对应表里没有找到符合的SKU，可能是设置错误")
                #ImportTradeInfo("InsertTrade error: no lesson match tradeID: %d %s %d" % (trade.ID, trade.Name, trade.ChannelID), "InsertTrade")
                return

            trade.ThirdPartyID = third_party.ID
            trade.LessonCategoryID = third_party.LessonCategoryID
            relations = LessonsRelation.objects.filter(ThirdPartyID = trade.ThirdPartyID)
            if not relations:
                ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", "%s %s" % (trade.Name, trade.SKUName) , None, "此订单没有对应的大指课程，不需要导入")
                trade.IsImported = True
                return
            
            lessons = []
            for relation in relations:
                lesson = Lesson.objects.get(ID=relation.LessonID)
                lessons.append({"Name":lesson.Name, "TeachingPlan":lesson.TeachingPlan})

            url="http://47.101.39.80/CreateDzhidianTrade/"
            data = {"mobile": user.Mobile, "lessons":json.dumps(lessons), "trade": json.dumps(tradeObj)}
            Log("InsertEdusohoAli %s" % data, "local", "0.0.0.0", "DEBUG")
            #s = requests.session()
            #s.keep_alive = False

            
            resp = None
            
            
            #with requests.Session() as s:
            #    resp = s.post(url,data,headers=http_header)
            #resp = requests.post(url, data, headers=http_header)
            resp = PostJ(url,data)
            Log("InsertEdusohoAli resp %s " % resp, "local", "0.0.0.0", "DEBUG")
            #Log("InsertEdusohoAli content %s " % resp.content, "local", "0.0.0.0", "DEBUG")
            ali_res = json.loads(resp)
            Log("InsertEdusohoAli res %s " % ali_res, "local", "0.0.0.0", "DEBUG")
            sentInfo = None
            
            if third_party.TelMsgTemplateID > 0 and ali_res.get('sent') == 1:
                sentInfo = '发送失败'
                try:
                    telMsgTemplates = getVar("TelMsgTemplate")
                    templates = telMsgTemplates.filter(MsgID=third_party.TelMsgTemplateID)
                    Log("InsertEdusohoAli templates %s " % templates[0].Content, "local", "0.0.0.0", "DEBUG")
                    if templates:
                        res = Send106txtTelMsg(user.Mobile,templates[0].Content, 1)
                        if res == '1':
                            sentInfo = '发送成功'
                        else:
                            sentInfo = res
                except Exception, e:
                    Log("CreateDzhidianTradeAli SendTelMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
            if third_party.wxMsgTemplateIDs is not None and third_party.wxMsgTemplateIDs != '' and ali_res.get('sent') == 1:
                sentInfo = '发送失败'
                try:
                    template_ids = third_party.wxMsgTemplateIDs.split(',')
                    for template_id in template_ids:
                        wx_user = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5', Mobile = user.Mobile)
                        wxObj = wxAccountInterface.wxAccountInterface(wx_user[0].SourceAccount)
                        res = wxObj.CallTemplateMessage(template_id, wx_user[0].openID, wx_user[0].Name, trade.Name, wx_user[0].Mobile or "您绑定的手机号")
                        if res['errcode'] == 0:
                            sentInfo = '发送成功'
                        else:
                            sentInfo = res
                except Exception, e:
                    Log("CreateDzhidianTradeAli SendwxMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
            if trade.ChannelID == 15 and ali_res.get('sent') == 1:
                temp_sentInfo = '小程序发送失败'
                try:
                    paraDic = {
                        "keyword1": user.Mobile,
                        "keyword2": 'waitan2016',
                        "keyword3": "%s 您好，感谢您对外滩的信任。\n\n您购买的课程现已开通~\n\n您可以登录www.ddianke.com进行观看；或者立即关注我们的服务号【外滩云课堂】获取更多课程信息。\n\n直播课学员请耐心等待工作人员联系。\n\n如有任何问题请添加小助手微信：tbe009"%user.Name
                    }
                    wx_user = wxUser.objects.get(SourceAccount = 'wxf11978168e04aba2', Mobile = user.Mobile)
                    template_id = '3tu5yLR2bzdJutFPH-viY1BROdQl8yiW2qBCXNyvLPo'
                    res = wxUtils.SendTemplateMsg(wx_user.openID, template_id, paraDic)
                    if res['errcode'] == 0:
                        temp_sentInfo = '小程序发送成功'
                    else:
                        temp_sentInfo = res['errmsg']
                    sentInfo = temp_sentInfo
                except Exception, e:
                    Log("CreateDzhidianTradeAli SendMiniappMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
                try:
                    temp_sentInfo = '服务号发送失败'
                    paraDic = {
                        "keyword1": user.Mobile,
                        "keyword2": 'waitan2016',
                        "keyword3": "%s 您好，感谢您对外滩的信任。\n\n您购买的课程现已开通~\n\n您可以登录www.ddianke.com进行观看；或者立即关注我们的服务号【外滩云课堂】获取更多课程信息。\n\n直播课学员请耐心等待工作人员联系。\n\n如有任何问题请添加小助手微信：tbe009"%user.Name
                    }
                    wx_user = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5', Mobile = user.Mobile)
                    if not wx_user:
                        temp_sentInfo = '没绑定服务号'
                    else:
                        wxObj = wxAccountInterface.wxAccountInterface(wx_user[0].SourceAccount)
                        paraDic = {
                            "keyword1": user.Mobile,
                            "keyword2": 'waitan2016',
                            "first": "%s 您好，感谢您对外滩的信任。\n\n您购买的课程现已开通~\n\n您可以登录www.ddianke.com进行观看；或者进入右下角的个人中心查看我的课程。\n\n直播课学员请耐心等待工作人员联系。\n"%user.Name,
                            "remark":"\n如有任何问题请添加小助手微信：tbe009",
                            "url":"http://www.ddianke.com/"
                        }
                        res = wxObj.CallCustomerTemplateMessage('5G_d1vrOyZM2Q_FRQTY2JeH2vQcP_MCGgann_zDlfVg', wx_user[0].openID, paraDic)
                        if res['errcode'] == 0:
                            temp_sentInfo = '服务号发送成功'
                        else:
                            temp_sentInfo = res
                    sentInfo += ";%s"%temp_sentInfo
                except Exception, e:
                    Log("CreateDzhidianTradeAli SendServiceMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
            ImportTradeDetail(trade.TradeID, trade.ChannelID, ali_res['isSuccess'], ali_res['failedType'], trade.Name, ali_res["Mobile"], ali_res['info'], sentInfo)
            Log("reimport: %s" % ali_res.get('reimport'), Type="DEBUG")
            if not ali_res.get('reimport'):
                trade.IsImported = True
                #if ali_res.get('is_new_trade'):
                #    trade.IsNewUserTrade = 1

def CreateDzhidianTrade(admin, trade):
    lessons = getVar("Lesson")
    lessons_of_third_party = getVar("LessonsOfThirdParty")
    lessons_relation = getVar("LessonsRelation")
    connection2 = pymysql.connect(**config)
    try:               
        with connection2.cursor() as cursor:
            #开课
            curr_time=time.time()
            time_local = time.localtime(curr_time)
            user = User.objects.get(ID = trade.UserID)
            cursor.execute("select * from user where verifiedMobile = '%s'" % user.Mobile)
            trade_user = cursor.fetchone()
            Log("CreateDzhidianTrade 1", Type="DEBUG")
            #又要考虑sku #不再考虑sku
            third_partys = lessons_of_third_party.filter(Name=trade.Name, ChannelID=trade.ChannelID)
            if third_partys is None or len(third_partys) == 0:
                ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", trade.Name, None, "对应表里没有找到符合的课程名，可能是代理销售课程")
                #ImportTradeInfo("InsertTrade error: no lesson match tradeID: %d %s %d" % (trade.ID, trade.Name, trade.ChannelID), "InsertTrade")
                return
            third_party = None
            for third_party_i in third_partys:
                if third_party_i.SKUName:
                    if third_party_i.SKUName == trade.SKUName:
                        third_party = third_party_i
                else:
                    third_party = third_party_i
            Log("CreateDzhidianTrade 2", Type="DEBUG")
            #third_party = third_partys[0]
            if not third_party:
                ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", "%s %s" % (trade.Name, trade.SKUName) , None, "对应表里没有找到符合的SKU，可能是设置错误")
                #ImportTradeInfo("InsertTrade error: no lesson match tradeID: %d %s %d" % (trade.ID, trade.Name, trade.ChannelID), "InsertTrade")
                return
                
            trade.ThirdPartyID = third_party.ID
            trade.LessonCategoryID = third_party.LessonCategoryID
            relations = lessons_relation.filter(ThirdPartyID = trade.ThirdPartyID)
            if not relations:
                ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", "%s %s" % (trade.Name, trade.SKUName) , None, "此订单没有对应的大指课程，不需要导入")
                return
                
            lessonDic = {}
            for relation in relations:
                lesson = lessons.get(ID=relation.LessonID)
                lessonDic[lesson.ID] = lesson
                #lesson_names.append(lessons.get(ID=relation.LessonID).Name)
            Log("CreateDzhidianTrade 3", Type="DEBUG")
            for key in lessonDic.keys():
                lesson_name = lessonDic[key].Name
                lesson_plan = lessonDic[key].TeachingPlan
                cursor.execute("select * from course_set_v8 where title = '%s'" % lesson_name)
                
                course_set_v8 = cursor.fetchone()
                if course_set_v8 is None:
                    ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", lesson_name, None, "大指上没有找到对应的课程名，可能是课程设置错误")
                    #ImportTradeInfo("InsertTrade no lesson name match on edusoho tradeID: %d %s" % (trade.ID, lesson_name), "InsertTrade")
                    return 
                
                get_v8_sql = "select * from course_v8 where courseSetId = %d" % course_set_v8['id']
                if lesson_plan is not None and lesson_plan != '':
                    get_v8_sql += " and title = '%s'" % lesson_plan
                cursor.execute(get_v8_sql)
                course_v8 = cursor.fetchone()
                if course_v8 is None:
                    ImportTradeDetail(trade.TradeID, trade.ChannelID, False, "课程错误", "%s %s" % (lesson_name,lesson_plan), None, "对应表里没有找到符合的学习计划，可能是课程设置错误")
                    #ImportTradeInfo("InsertTrade no lesson plan match tradeID: %d %s" % (trade.ID, lesson_name), "InsertTrade")
                    return
                    
                sn = time.strftime("%Y%m%d%H%M%S",time_local) + str(datetime.datetime.now().microsecond)
                    
                #确定有课再添加用户
                if trade_user is None:
                    trade_user = CreateDzhidianUser(connection2, cursor, admin, user)
                    #trade.IsNewUserTrade = True
                title = course_set_v8['title'] + '-' + course_v8['title']
                price_int = int(course_v8['price'] * 100)
                biz_order_id = 0
                refund_time = 0
                
                cursor.execute("SELECT * FROM course_member WHERE courseId = %d and userId = %d" % (course_v8['id'], trade_user['id']))
                course_member = cursor.fetchone()
                if course_member is not None:
                    ImportTradeDetail(trade.TradeID, trade.ChannelID, True, "撤销导入", lesson_name, None, "对应的课程已经开通，不需要再次导入")
                    #ImportTradeInfo("InsertTrade already had this lesson tradeID = %d courseId = %d and userId = %d" % (trade.ID, course_v8['id'], trade_user['id']), "InsertTrade")
                    continue
                
                #Log("InsertEdusoho idFree: %d" % course_v8['isFree'], "local", "0.0.0.0", "DEBUG")
                if course_v8['isFree'] != 1:
                    #order 免费的课不需要order
                    insert_biz_order = "INSERT INTO biz_order (title, user_id, source, price_type, created_reason, create_extra,status, sn, price_amount, pay_amount, created_user_id, created_time, updated_time) VALUES ('%s', %d, 'outside', 'CNY', 'import', '{\"queryfield\":\"%s\",\"price\":\"%d\",\"remark\":\"import\",\"source\":\"outside\",\"userId\":\"%d\"}','%s', '%s', %d, %d, %d, %d, %d)" \
                        % (title, trade_user['id'], trade_user['verifiedMobile'], course_v8['price'], trade_user['id'], 'finished', sn, price_int, price_int, admin['id'], curr_time, curr_time)
                    cursor.execute(insert_biz_order)
                    biz_order_id = connection2.insert_id()
                    insert_biz_order_item = "INSERT INTO biz_order_item (target_id, target_type, price_amount, pay_amount, status, title, num, unit, create_extra, snapshot, order_id, seller_id, user_id, sn, created_time, updated_time) VALUES (%d, 'course', %d, %d, '%s', '%s', '1', '', '', '', '1', '0', %d, '%s', %d, %d)" \
                        % (course_v8['id'], price_int, price_int, 'finished', title, trade_user['id'], sn, curr_time, curr_time)
                    cursor.execute(insert_biz_order_item)
                    insert_biz_order_log = "INSERT INTO biz_order_log (status, order_id, user_id, deal_data, ip, created_time, updated_time) VALUES ('order.created', %d, %d, '', '', %d, %d)" \
                        % (biz_order_id, admin['id'], curr_time, curr_time)
                    cursor.execute(insert_biz_order_log)
                #退款时间 864000, operator_id
                refund_time = curr_time + 864000
                dead_line = 0
                if course_v8['expiryMode'] == 'days':
                    dead_line = curr_time + course_v8['expiryDays'] * 24 * 3600
                if course_v8['expiryMode'] == 'date':
                    dead_line = course_v8['expiryEndDate']
                operator_id = admin['id']
                
                #course                        
                update_course_v8 = "UPDATE course_v8 SET studentNum = %d, updatedTime = %d WHERE id = %d" % (course_v8['studentNum'] + 1, curr_time, course_v8['id'])
                cursor.execute(update_course_v8)
                update_course_set_v8 = "UPDATE course_set_v8 SET studentNum = %d, updatedTime = %d WHERE id = %d" % (course_set_v8['studentNum'] + 1, curr_time, course_set_v8['id'])
                cursor.execute(update_course_set_v8)
                #去重
                
                member_id = 0
                if course_member is None:
                    insert_course_member = "INSERT INTO course_member (courseId, userId, courseSetId, orderId, noteNum, deadline, levelId, role, remark, createdTime, refundDeadline, updatedTime, noteLastUpdateTime) VALUES (%d, %d, %d, %d, %d, %d, '0', 'student', 'import', %d, %d, %d, %d)" \
                        % (course_v8['id'], trade_user['id'], course_set_v8['id'], biz_order_id, 0, dead_line, curr_time, refund_time, curr_time, curr_time)
                    cursor.execute(insert_course_member)
                    member_id = connection2.insert_id()
                else:
                    member_id = course_member['id']
                data = '{\"member\":{\"id\":\"%d\",\"courseId\":\"%d\",\"classroomId\":\"0\",\"joinedType\":\"course\",\"userId\":\"%d\",\"orderId\":\"%d\",\"deadline\":\"%d\",\"refundDeadline\":\"%d\",\"levelId\":\"0\",\"learnedNum\":\"0\",\"learnedCompulsoryTaskNum\":\"0\",\"credit\":\"0\",\"noteNum\":\"0\",\"noteLastUpdateTime\":\"0\",\"isLearned\":\"0\",\"finishedTime\":\
                \"0\",\"seq\":\"0\",\"remark\":\"import\",\"isVisible\":\"1\",\"role\":\"student\",\"locked\":\"0\",\"deadlineNotified\":\"0\",\"createdTime\":\"%d\",\"lastLearnTime\":null,\"updatedTime\":\"%d\",\"lastViewTime\":\"0\",\"courseSetId\":\"%d\"}}' \
                    % (member_id, course_v8['id'], trade_user['id'], biz_order_id, dead_line, refund_time, curr_time, curr_time, course_set_v8['id'])
                insert_member_operation_record = "INSERT INTO member_operation_record (user_id, member_id, member_type, target_id, target_type, operate_type, operate_time, operator_id, data, order_id, title, course_set_id, parent_id, join_course_set, reason, reason_type, created_time) VALUES (%d, %d, '%s', %d, '%s', '%s', %d, %d, '%s', %d, '%s', %d, %d, %d, '%s', '%s', %d)" \
                    % (trade_user['id'], member_id, 'student', course_v8['id'], 'course' , 'join', curr_time, operator_id, data, biz_order_id, course_v8['title'],  course_set_v8['id'], course_set_v8['parentId'], 1, 'site.join_by_import', 'import_join', curr_time)
                cursor.execute(insert_member_operation_record)
                properties = '{\"course\":{\"id\":\"%d\",\"title\":\"%s\",\"type\":\"normal\",\"rating\":\"0\",\"price\":\"%d\"}}' \
                    % (course_v8['id'], course_v8['title'], course_v8['price'])
                insert_status = "INSERT INTO status (type, courseId, objectType, objectId, private, userId, properties, createdTime, message) VALUES ('become_student', %d, 'course', %d, '0', %d, '%s', %d, '')" \
                    % (course_v8['id'], course_v8['id'], trade_user['id'], properties, curr_time)
                cursor.execute(insert_status)
            sentInfo = None
            Log("CreateDzhidianTrade 4", Type="DEBUG")
            if third_party.TelMsgTemplateID > 0:
                sentInfo = '发送失败'
                try:
                    telMsgTemplates = getVar("TelMsgTemplate")
                    templates = telMsgTemplates.filter(MsgID=third_party.TelMsgTemplateID)
                    if templates:
                        res = Send106txtTelMsg(user.Mobile,templates[0].Content, 1)
                        if res == '1':
                            sentInfo = '发送成功'
                        else:
                            sentInfo = res
                except Exception, e:
                    Log("CreateDzhidianTrade SendTelMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
            if third_party.wxMsgTemplateIDs is not None and third_party.wxMsgTemplateIDs != '':
                sentInfo = '发送失败'
                try:
                    template_ids = third_party.wxMsgTemplateIDs.split(',')
                    for template_id in template_ids:
                        wx_user = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5',Mobile = user.Mobile)
                        wxObj = wxAccountInterface.wxAccountInterface(wx_user[0].SourceAccount)
                        res = wxObj.CallTemplateMessage(template_id, wx_user[0].openID, wx_user[0].Name, trade.Name, wx_user[0].Mobile or "您绑定的手机号")
                        if res['errcode'] == 0:
                            sentInfo = '发送成功'
                        else:
                            sentInfo = res
                except Exception, e:
                    Log("CreateDzhidianTrade SendwxMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
            if trade.ChannelID == 15:
                temp_sentInfo = '小程序发送失败'
                try:
                    paraDic = {
                        "keyword1": user.Mobile,
                        "keyword2": 'waitan2016',
                        "keyword3": "%s 您好，感谢您对外滩的信任。\n\n您购买的课程现已开通~\n\n您可以登录www.ddianke.com进行观看；或者立即关注我们的服务号【外滩云课堂】获取更多课程信息。\n\n直播课学员请耐心等待工作人员联系。\n\n如有任何问题请添加小助手微信：tbe009"%user.Name
                    }
                    wx_user = wxUser.objects.get(SourceAccount = 'wxf11978168e04aba2', Mobile = user.Mobile)
                    template_id = '3tu5yLR2bzdJutFPH-viY1BROdQl8yiW2qBCXNyvLPo'
                    res = wxUtils.SendTemplateMsg(wx_user.openID, template_id, paraDic)
                    if res['errcode'] == 0:
                        temp_sentInfo = '小程序发送成功'
                    else:
                        temp_sentInfo = res['errmsg']
                    sentInfo = temp_sentInfo
                except Exception, e:
                    Log("CreateDzhidianTradeAli SendMiniappMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
                try:
                    temp_sentInfo = '服务号发送失败'
                    paraDic = {
                        "keyword1": user.Mobile,
                        "keyword2": 'waitan2016',
                        "keyword3": "%s 您好，感谢您对外滩的信任。\n\n您购买的课程现已开通~\n\n您可以登录www.ddianke.com进行观看；或者立即关注我们的服务号【外滩云课堂】获取更多课程信息。\n\n直播课学员请耐心等待工作人员联系。\n\n如有任何问题请添加小助手微信：tbe009"%user.Name
                    }
                    wx_user = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5', Mobile = user.Mobile)
                    if not wx_user:
                        temp_sentInfo = '没绑定服务号'
                    else:
                        wxObj = wxAccountInterface.wxAccountInterface(wx_user[0].SourceAccount)
                        paraDic = {
                            "keyword1": user.Mobile,
                            "keyword2": 'waitan2016',
                            "first": "%s 您好，感谢您对外滩的信任。\n\n您购买的课程现已开通~\n\n您可以登录www.ddianke.com进行观看；或者进入右下角的个人中心查看我的课程。\n\n直播课学员请耐心等待工作人员联系。\n"%user.Name,
                            "remark":"\n如有任何问题请添加小助手微信：tbe009",
                            "url":"http://www.ddianke.com/"
                        }
                        res = wxObj.CallCustomerTemplateMessage('5G_d1vrOyZM2Q_FRQTY2JeH2vQcP_MCGgann_zDlfVg', wx_user[0].openID, paraDic)
                        if res['errcode'] == 0:
                            temp_sentInfo = '服务号发送成功'
                        else:
                            temp_sentInfo = res
                    sentInfo += ";%s"%temp_sentInfo
                except Exception, e:
                    Log("CreateDzhidianTradeAli SendServiceMsg error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
            ImportTradeDetail(trade.TradeID, trade.ChannelID, True, "导入成功", trade.Name, None, "课程导入成功", sentInfo)
            #ImportTradeInfo("InsertTrade success tradeID: %d  %s" % (trade.ID, trade.TradeID), "InsertTrade")
            user.IsImported = True
            user.save()
            connection2.commit()
    except Exception, e:
        #ImportTradeInfo(e, "CreateDzhidianTrade")
        #处理错误，需要一张错误处理表
        Log("CreateDzhidianTrade error tradeID: %s %s" % (trade.TradeID, e), "local", "0.0.0.0", "DEBUG")
        connection2.rollback()
        return 'error'
    finally:
        connection2.close()
        
def CreateDzhidianUser(connection, cursor, admin, user):
    salt = 'lxckxyplbxcgcsw0g0ss0084g84g0og'
    password = 'izFY62tBlRDNzH2vZbAEqbUAxZZlYbeXEchy+CJp1Lc='
    curr_time=time.time()
    #下面几项都要判断去重
    email = 'user_%s@edusoho.net' % random_str2(9)
    uuid = random_uuid(40)
    nickname = "user%s" % random_str2(6)
    insert_user = "INSERT INTO user (verifiedMobile, email, emailVerified, nickname, createdIp, registeredWay, roles, type, createdTime, salt, password, setup, uuid, updatedTime) VALUES ('%s', '%s', '0', '%s', '', '', '|ROLE_USER|', 'import', %d, '%s', '%s', '1', '%s', %d)" \
    % (user.Mobile, email, nickname, curr_time, salt, password, uuid, curr_time)
    cursor.execute(insert_user)
    cursor.execute("select id,nickname from user where verifiedMobile = '%s'" % user.Mobile)
    new_user = cursor.fetchone()
    insert_user_profile = "INSERT INTO user_profile (id, mobile, idcard, truename, company, job, weixin, weibo, qq, site, gender, intField1, dateField1, floatField1, intField2, dateField2, floatField2, intField3, dateField3, floatField3, intField4, dateField4, floatField4, intField5, dateField5, floatField5, varcharField1, textField1, varcharField2, textField2, varcharField3, textField3, \
    varcharField4, textField4, varcharField5, textField5, varcharField6, textField6, varcharField7, textField7, varcharField8, textField8, varcharField9, textField9, varcharField10, textField10) VALUES (%d, '%s', '', '', '', '', '', '', '', '', 'secret', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '')" \
    % (new_user['id'], user.Mobile)
    cursor.execute(insert_user_profile)
    insert_message = "INSERT INTO message (fromId, toId, type, content, createdTime) VALUES (%d, %d, 'text', '您好%s，我是EduSoho网络课堂的管理员，欢迎加入EduSoho网络课堂，祝您学习愉快。如有问题，随时与我联系。', %d)" \
    % (admin['id'], new_user['id'], new_user['nickname'], curr_time)
    cursor.execute(insert_message)
    message_id = connection.insert_id()
    insert_message_conversation = "INSERT INTO message_conversation (fromId, toId, messageNum, latestMessageUserId, latestMessageContent, latestMessageTime, unreadNum, createdTime) VALUES (%d, %d, '1', %d, '您好%s，我是EduSoho网络课堂的管理员，欢迎加入EduSoho网络课堂，祝您学习愉快。如有问题，随时与我联系。', %d, '1', %d)" \
    % (admin['id'], new_user['id'], admin['id'], new_user['nickname'], curr_time, curr_time)
    cursor.execute(insert_message_conversation)
    message_conversation_id = connection.insert_id()
    insert_message_relation = "INSERT INTO message_relation (conversationId, messageId, isRead) VALUES (%d, %d, '0')" % (message_conversation_id, message_id)                 
    cursor.execute(insert_message_relation)
    update_user = "UPDATE user SET newMessageNum = newMessageNum + '1' WHERE id = %d" % new_user['id']
    cursor.execute(update_user)
    insert_biz_pay_user_balance = "INSERT INTO biz_pay_user_balance (user_id, created_time, updated_time) VALUES (%d, %d, %d)" % (new_user['id'], curr_time, curr_time)
    cursor.execute(insert_biz_pay_user_balance)

    cursor.execute("select * from user where verifiedMobile = '%s'" % user.Mobile)
    trade_user = cursor.fetchone()
    return trade_user

def UpdateXiaoeTradesByPage(page=0):
    try:
        pagesize = 300
        xiaoeSDK = XiaoeSDK(app_id = 'appj7VCGP4T4314', app_secret = 'ZGI2FL7dzLXjZVBrp1wFOrgh9r5z5lxP')
        cmd = 'order.list.get'
        start_date = (datetime.datetime.today() + datetime.timedelta(days = -3)).strftime("%Y-%m-%d")
        end_date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")#.strftime("%Y-%m-%d")
        paramsDic = {
            "page_size": pagesize,
            "begin_time": start_date,
            "end_time": end_date,
            "order_state": 1,
            "page_index": page,
            #"product_id": "p_59547ad379b4b_1rsVo09s",
            #"user_id":"u_5a7901ad83dd9_cbjY6chqBH"
        }
        res = xiaoeSDK.send(cmd, paramsDic, use_type = 3, version = '2.0')
        Log("UpdateXiaoeTradesByPage %s"% res, "local", "0.0.0.0", "DEBUG")
        if res['msg'] == 'success':
            data = res['data']
            for item in data:
                SaveXiaoeTrade(item)
            if len(data) == pagesize:
                page += 1
                UpdateXiaoeTradesByPage(page)
                #Log("UpdateXiaoeTradesByPage 1 %s"% item['title'], "local", "0.0.0.0", "DEBUG")
            #return HttpResponse(data)
        Log("UpdateXiaoeTradesByPage success", "local", "0.0.0.0", "DEBUG")
    except Exception, e:
        #ImportTradeInfo(e, "UpdateXiaoeTradesByPage")
        Log("UpdateXiaoeTradesByPage error:%s"%e, "local", "0.0.0.0", "DEBUG")

def GetXiaoeUser(user_id):
    xiaoeSDK = XiaoeSDK(app_id = 'appj7VCGP4T4314', app_secret = 'ZGI2FL7dzLXjZVBrp1wFOrgh9r5z5lxP')
    cmd = 'users.getinfo'
    paramsDic = {
        "user_id": user_id
    }
    res = xiaoeSDK.send(cmd, paramsDic, use_type = 3, version = '1.0')
    #Log("GetXiaoeUser %s"% res, "local", "0.0.0.0", "DEBUG")
    if res['msg'] == 'success':
        return res['data'][0]
    else:
        return None

def SaveXiaoeTrade(item):
    tradeInfo = TradeInfo.objects.filter(TradeID = item['order_id'])
    channel = getVar('Channel').filter(Name='xiaoe')[0]
    IsImported = False
    if tradeInfo:
        return
    user_info = GetXiaoeUser(item['user_id'])
    if user_info is None:
        ImportTradeDetail(item['order_id'],channel.ID,False, "用户错误", item['title'], None, "没有查到符合user_id的用户")
        #ImportTradeInfo("SaveXiaoeTrade no user or mobile user: %s"% user_info, "SaveXiaoeTrade")
        #ImportTradeInfo("SaveXiaoeTrade no user or mobile trade: %s"% item, "SaveXiaoeTrade")
        return
    if user_info['phone'] is None or user_info['phone'] == '':
        ImportTradeDetail(item['order_id'],channel.ID,False, "电话错误", item['title'], user_info['phone'], "用户没有提供电话")
        #ImportTradeInfo("SaveXiaoeTrade mobile is illegal user: %s"% user_info, "SaveXiaoeTrade")
        #ImportTradeInfo("SaveXiaoeTrade mobile is illegal trade: %s"% item, "SaveXiaoeTrade")
        return
    if VerifyMobile(user_info['phone']) == False:
        ImportTradeDetail(item['order_id'],channel.ID,False, "电话错误", item['title'], user_info['phone'], "电话格式错误")
        #ImportTradeInfo("SaveXiaoeTrade mobile is illegal user: %s"% user_info, "SaveXiaoeTrade")
        #ImportTradeInfo("SaveXiaoeTrade mobile is illegal trade: %s"% item, "SaveXiaoeTrade")
        IsImported = True #电话异常的用户
        
    #Log("SaveXiaoeTrade %s"% item, "local", "0.0.0.0", "DEBUG")
    
    

    mobile = user_info['phone']
    name = user_info['nickname']
    openid = user_info['wx_open_id']

    user = getVar('User').filter(Mobile=mobile)
    is_first_order = False
    #Log("SaveXiaoeTrade %s"% user, "local", "0.0.0.0", "DEBUG")
    if not user:
        user = User(IsImported=IsImported, Name=name, Mobile=mobile, ChannelID=channel.ID, DistributorName=None)
        user.save()
        updateVar('User')
        user = getVar('User').filter(Mobile=mobile)[0]
        is_first_order = True
        #Log("SaveXiaoeTrade id %s"% user.pk, "local", "0.0.0.0", "DEBUG")
    else:
        user = user[0]
        if name and name != ' ':
            user.Name = name
            user.save()
            
    #Log("SaveXiaoeTrade %s"% user.Name, "local", "0.0.0.0", "DEBUG")
    payment = item['price'] / 100.0
    discount_fee = 0.00#item['coupon_price'] / 100.0
    trade = TradeInfo(UserID=user.ID, IsImported=IsImported, TradeID=item['order_id'], ChannelID=channel.ID, ProdCount=1, Name=item['title'], 
                     PayType=item['payment_type'], OuterTradeID=item['out_order_id'], Created=item['created_at'], Updated=item['created_at'],
                     Payment=payment, DiscountFee=discount_fee, DistributorName=None, IsNewUserTrade=is_first_order)
    trade.save()
    
    
def UpdateYouzanTradesByPage(page_no=1):
    youzan_token = GetYouzanToken()
    #现有逻辑是已发货才导入
    trade_status = "WAIT_BUYER_CONFIRM_GOODS"
    start_date = (datetime.datetime.today() + timedelta(days = -3)).strftime("%Y-%m-%d")
    end_date = urllib.quote(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))#.strftime("%Y-%m-%d")
    #trade_status = "TRADE_SUCCESS"
    #start_date = '2018-06-01'
    #end_date = '2018-06-05'
    url = """https://open.youzan.com/api/oauthentry/youzan.trades.sold/3.0.0/get?access_token=%s&start_created=%s&end_created=%s&status=%s&page_no=%d&page_size=30&use_has_next=true""" % (youzan_token,start_date,end_date,trade_status,page_no)
    Log("UpdateYouzanTrades %s"% url, "local", "0.0.0.0", "DEBUG")
    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req)
    res = json.loads(res_data.read().decode('utf-8'))
    #Log("UpdateYouzanTrades response %s"%res, "local", "0.0.0.0", "DEBUG")
    data = res['response']['trades']
    #Log("UpdateYouzanTrades length %d"% len(data), "local", "0.0.0.0", "DEBUG")
    for item in data:
        SaveYouzanTrade(item)

    if res['response'].has_key('has_next') and res['response']['has_next'] == True:
        UpdateYouzanTradesByPage(page_no+1)
    Log("UpdateYouzanTrades end %d" % len(data), "local", "0.0.0.0", "DEBUG")

def SaveYouzanTrade(item):
    tradeInfo = TradeInfo.objects.filter(TradeID = item['tid'])
    if tradeInfo:
        return
    channel = getVar('Channel').filter(Name='youzan')[0]
    orders = item['orders']
    IsImported=False
    for order in orders:
        order_title = item['title']
        if order['title']:
            order_title = order['title']
        mobile = item['receiver_mobile']
        name = item['receiver_name']
        #if not name:
        #    fans_info = item['fans_info']
        #    name = fans_info['fans_nickname'].encode('utf-8', 'ignore')
        child_name = ''
        buyer_info = order['buyer_messages']
        wechat_code = ''
        age = 0
        grade = 0
        if len(buyer_info) > 0:
            for info in buyer_info:
                if info['title'] == '手机号' or info['title'] == '手机号码':
                    mobile = info['content']
                elif info['title'] == '学生姓名' or info['title'] == '姓名':
                    child_name = info['content']
                    if not name:
                        name = child_name
                elif info['title'] == '微信号':
                    wechat_code = info['content']
                elif info['title'] == '学生年龄':
                    try:
                        age = int(info['content'])
                    except:
                        age = 0
                elif info['title'].startswith('学生年级'):
                    try:
                        grade = int(info['content'])
                    except:
                        grade = 0
            #Log("buyer_info %s; %s; %s; %s"% (buyer_info,mobile,name,wechat_code), "local", "0.0.0.0", "DEBUG")
        if mobile is None or mobile == '':
            if item['tid'] == 'E20181226134738087200047':
                return
            ImportTradeDetail(item['tid'], channel.ID, False, "电话错误", item['title'], mobile, "用户没有提供电话或者电话格式不对")
            return
        if VerifyMobile(mobile) == False:
            ImportTradeDetail(item['tid'], channel.ID, False, "电话错误", item['title'], mobile, "电话格式错误")
            IsImported = True #电话错误的直接设为已经导入，然后手动操作
            #return 
            
        relations = None
        distributorName = None
        distributorID = None
        distributorType = None
        if item['type'] == "BULK_PURCHASE":
            fans_info = item['fans_info']
            if item['relations']:
                relations = ','.join(item['relations'])
            if fans_info:
                if fans_info.has_key('fans_nickname'):
                    distributorName = fans_info['fans_nickname']
                if fans_info.has_key('fans_id'):
                    distributorID = fans_info['fans_id']
                if fans_info.has_key('fans_type'):
                    distributorType = str(fans_info['fans_type'])
                    
        user = User.objects.filter(Mobile=mobile)
        
        #创建订单时就加入课程对照ID信息
        third_partyid = None
        lesson_category_id = None
        channelID = channel.ID
        third_partys = LessonsOfThirdParty.objects.filter(Name=order_title, ChannelID=channel.ID)
        if third_partys:
            third_partyid = third_partys[0].ID
            lesson_category_id = third_partys[0].LessonCategoryID
        else:#找不到的都是买书渠道
            channelID = 6
        is_first_order = False
        if not user:
            area = GetUserAreaByMobile(mobile)
            province = item['receiver_state']
            city = item['receiver_city']
            user_zip = item['receiver_zip']
            segmentName = ''
            if type(area) is dict:
                #Log("SaveYouzanTrade area %s" % area, Type="DEBUG")
                province = area.get('province', '')
                city = area.get('cityName', '')
                user_zip = area.get('postCode', '')
                segmentName = area.get('segmentName', '')
            user = User(IsImported=IsImported, Name=name, Mobile=mobile, ChannelID=channelID, Province=province, 
                       City=city, District=item['receiver_district'], Address=item['receiver_address'], NickName=None, ChildAge = age, ChildGrade = grade,
                       Zip=user_zip, DistributorName=distributorName, Created=item['pay_time'], SegmentName=segmentName,ChildName=child_name)
            user.save()
            is_first_order = True
            
            #updateVar('User')
            #user = getVar('User').filter(Mobile=mobile)[0]
            #Log("SaveYouzanTrade id %s"% user.pk, "local", "0.0.0.0", "DEBUG")
        else:
            user = user[0]
            if name and name != ' ':
                user.Name=name
                user.ChildName=child_name
            if age:
                user.ChildAge=age
            if grade:
                user.ChildGrade=grade
            user.save()
        
   
        trade = TradeInfo(IsImported=IsImported, UserID=user.ID, TradeID=item['tid'], ChannelID=channelID, OrderCount=item['num'], Name=order_title, 
                         TradeType=item['type'], BuyerMessage=item['buyer_message'], TradeMessage=item['trade_memo'],
                         FeedBack=item['feedback'], OuterTradeID=item['outer_tid'], TransactionID=item['transaction_tid'],
                         Status=item['status'], TotalFee=item['total_fee'], PostFee=item['post_fee'], RefundedFee=item['refunded_fee'],
                         DiscountFee=item['discount_fee'], Payment=item['payment'], Created=item['created'], Updated=item['update_time'], 
                         PayTime=item['pay_time'], PayType=item['pay_type'], TuanNo=item['tuan_no'], IsTuanHead=item['is_tuan_head'],
                         OrderID=order['oid'], ProdID=order['item_id'], SKUID=order['sku_id'], SKUCode=order['sku_unique_code'], SKUName=order['sku_properties_name'],
                         ProdCount=order['num'], OuterSKUID=order['outer_sku_id'], OuterProdID=order['outer_item_id'], DistributorName=distributorName, 
                         DistributorID=distributorID, DistributorType=distributorType, Relations=relations, ThirdPartyID=third_partyid, IsNewUserTrade=is_first_order, LessonCategoryID=lesson_category_id)
        trade.save()
        
        ImportCloudCourseUser(trade, user)
        
def ImportCloudCourseUser(trade, user):
    try:
        courses = CloudCourse.objects.filter(Name=trade.Name)
        for course in courses:
            if ((not course.SKUName1 or course.SKUName1 in trade.SKUName) and (not course.SKUName2 or course.SKUName2 in trade.SKUName) and (not course.SKUName3 or course.SKUName3 in trade.SKUName) 
                and (not course.SKUName4 or course.SKUName4 in trade.SKUName) and (not course.SKUValue1 or course.SKUValue1 in trade.SKUName) and (not course.SKUValue2 or course.SKUValue2 in trade.SKUName) 
                and (not course.SKUValue3 or course.SKUValue3 in trade.SKUName) and (not course.SKUValue4 or course.SKUValue4 in trade.SKUName)):
                member = CloudCourseMember.objects.filter(CloudCourseID=course.ID, UserID=user.ID)
                if not member:
                    member = CloudCourseMember(CloudCourseID=course.ID, UserID=user.ID, Name=user.Name, Mobile=user.Mobile)
                    member.save()
                break
    except Exception,e:
        Log("ImportCloudCourseUser error: %s" % e, Type="DEBUG")
        
        
        
def UpdateEdusohoOrder(request):
    connection = pymysql.connect(**config)
    try:
        #url = "UpdateUserAndTradesFromEdusoho/"
        #queue = TaskQueue('queue_name')
        start_date = 0
        start_date = int(time.mktime(time.strptime((datetime.datetime.today() + timedelta(days = -3)).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")))
        channelID = 1
        trade_ids = []
        edusoho_orders = TradeInfo.objects.values('TradeID').filter(ChannelID = 1)
        for order in edusoho_orders:
            trade_ids.append("'%s'" % order['TradeID'])
        count = 0
        with connection.cursor() as cursor:
            cursor.execute("select * from course_member where orderId in (select id from biz_order where source = 'self' and createdTime > %d and sn not in (%s)) order by createdTime" % (start_date,','.join(trade_ids)))
            edusoho_course = cursor.fetchall()
            for course in edusoho_course:
                count += 1
                #user_ids.append("'%s'" % user['id'])
                cursor.execute("select * from user where id = %d" % course['userId'])
                course_user = cursor.fetchone()
                user = User.objects.filter(Mobile = course_user['verifiedMobile'])
                
                if not user:
                    userid = course_user['id']
                    nickname = course_user['nickname']
        
                    created = course_user['createdTime']
                    timeArray = time.localtime(created)
                    created = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        
                    lastvisited = course_user['loginTime']
                    timeArray = time.localtime(lastvisited)
                    lastvisited = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        
                    mobile = course_user['verifiedMobile']
                    area = GetUserAreaByMobile(mobile)
                    province = ''
                    city = ''
                    user_zip = ''
                    segmentName = ''
                    if type(area) is dict:
                        province = area.get('province', '')
                        city = area.get('cityName', '')
                        ser_zip = area.get('postCode', '')
                        segmentName = area.get('segmentName', '')
            
                    channelID = 1
                    

                    user = User(ChannelID=channelID, IsImported=1, Name=nickname,Province = province,City=city, Zip=user_zip, SegmentName=segmentName, Mobile=mobile, Created=created, LastLoginTime=lastvisited, EdusohoID=userid)
                    user.save()
                else:
                    user = user[0]

                curr_time=time.time()
                time_local = time.localtime(curr_time)
                trade_sn = "EdusohoOrder%s%s" % (time.strftime("%Y%m%d%H%M%S",time_local), str(datetime.datetime.now().microsecond))
                payment = 0
                pay_time = datetime.datetime.now()
                if course['orderId'] > 0:
                    cursor.execute("SELECT * FROM biz_order WHERE id = %d" % course['orderId'])
                    order = cursor.fetchone()
                    if order:
                        trade_sn = order['sn']
                        payment = order['pay_amount']/100
                        timeArray = time.localtime(order['pay_time'])
                        pay_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                title = ''
                sku = ''
                if course['courseId'] > 0:
                    cursor.execute("SELECT * FROM course_v8 WHERE id = %d " % course['courseId'])
                    course_v8 = cursor.fetchone()
                    if course_v8:
                        title = course_v8['courseSetTitle']
                        if course_v8['title'] != '默认教学计划':
                            sku = course_v8['title']
                            
                third_partyid = None
                third_partys = None
                lesson_category_id = None
                if sku:
                    third_partys = LessonsOfThirdParty.objects.filter(Name=title, ChannelID=channelID, SKUName=sku)
                else:
                    third_partys = LessonsOfThirdParty.objects.filter(Name=title, ChannelID=channelID, SKUName=None)
                if third_partys:
                    third_partyid = third_partys[0].ID
                    lesson_category_id = third_partys[0].LessonCategoryID
       
                trade = TradeInfo(IsImported=1, UserID=user.ID, TradeID=trade_sn, ChannelID=channelID, Name=title, 
                         Payment=payment, Created=pay_time, PayTime=pay_time, SKUName=sku, ThirdPartyID=third_partyid, LessonCategoryID=lesson_category_id)
                trade.save()

                #para = json.dumps(data,ensure_ascii=False).encode('utf-8')
                #queue.add(Task(url, para ,delay=2))
                #UpdateUserAndTradesFromEdusoho(user)
                #break;

            
            #count = len(edusoho_course)
        return HttpResponse(count)
    except Exception, e:
        #ImportTradeInfo(e, "InsertEdusoho")
        Log("InsertEdusoho error :%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    finally:
        connection.close()
        
        
def UpdateEdusohoUser(request):
    connection = pymysql.connect(**config)
    try:
        start_date = int(time.mktime(time.strptime((datetime.datetime.today() + timedelta(days = -3)).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")))
        count = 0
        curr_users = User.objects.values('Mobile')
        mobiles = []
        user_ids = []
        for curr_user in curr_users:
            mobiles.append("'%s'" % curr_user['Mobile'])
        url = "UpdateUserAndTradesFromEdusoho/"
        queue = TaskQueue('queue_name')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE roles = '|ROLE_USER|' and  VerifiedMobile not in (%s) and VerifiedMobile <> '' and createdTime > %d " % (','.join(mobiles), start_date))
            edusoho_users = cursor.fetchall()
            for user in edusoho_users:
                #user_ids.append("'%s'" % user['id'])
                count += 1
                data = {}
                data["userid"] = user['id']
                data["created"] = user['createdTime']
                data["lastViewTime"] = user['loginTime']
                data["mobile"] = user['verifiedMobile']
                data["nickname"] = user['nickname']
                para = json.dumps(data,ensure_ascii=False).encode('utf-8')
                queue.add(Task(url, para ,delay=2))
                #UpdateUserAndTradesFromEdusoho(user)
                #break;

            
            #count = len(edusoho_users)
        return HttpResponse(count)
    except Exception, e:
        #ImportTradeInfo(e, "InsertEdusoho")
        Log("InsertEdusoho error :%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    finally:
        connection.close()
        
@csrf_exempt
def UpdateUserAndTradesFromEdusoho(request):
    connection = pymysql.connect(**config)
    try:
        params = json.loads(request.raw_post_data)
        Log("UpdateUserAndTradesFromEdusoho user para %s " % params, Type="DEBUG")
        userid = int(params.get('userid'))
        nickname = params.get('nickname')
        
        created = int(params.get('created'))
        timeArray = time.localtime(created)
        created = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        
        lastvisited = int(params.get('lastViewTime'))
        timeArray = time.localtime(lastvisited)
        lastvisited = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        
        mobile = params.get('mobile')
        area = GetUserAreaByMobile(mobile)
        province = ''
        city = ''
        user_zip = ''
        segmentName = ''
        if type(area) is dict:
            province = area.get('province', '')
            city = area.get('cityName', '')
            user_zip = area.get('postCode', '')
            segmentName = area.get('segmentName', '')
            
        channelID = 1
        user = User.objects.filter(Mobile = mobile)
        if user:
            return HttpResponse("")
        user = User(ChannelID=channelID, IsImported=1, Name=nickname,Province = province,City=city, Zip=user_zip, SegmentName=segmentName, Mobile=mobile, Created=created, LastLoginTime=lastvisited, EdusohoID=userid)
        user.save()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM course_member WHERE userId = %d" % userid)
            edusoho_courses = cursor.fetchall()
            for course in edusoho_courses:
                curr_time=time.time()
                time_local = time.localtime(curr_time)
                trade_sn = "EdusohoOrder%s%s" % (time.strftime("%Y%m%d%H%M%S",time_local), str(datetime.datetime.now().microsecond))
                payment = 0
                pay_time = datetime.datetime.now()
                if course['orderId'] > 0:
                    cursor.execute("SELECT * FROM biz_order WHERE id = %d " % course['orderId'])
                    order = cursor.fetchone()
                    if order:
                        trade_sn = order['sn']
                        payment = order['pay_amount']/100
                        timeArray = time.localtime(order['pay_time'])
                        pay_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                
                title = ''
                sku = ''
                if course['courseId'] > 0:
                    cursor.execute("SELECT * FROM course_v8 WHERE id = %d " % course['courseId'])
                    course_v8 = cursor.fetchone()
                    if course_v8:
                        title = course_v8['courseSetTitle']
                        if course_v8['title'] != '默认教学计划':
                            sku = course_v8['title']
                            
                third_partyid = None
                third_partys = None
                lesson_category_id = None
                if sku:
                    third_partys = LessonsOfThirdParty.objects.filter(Name=title, ChannelID=channelID, SKUName=sku)
                else:
                    third_partys = LessonsOfThirdParty.objects.filter(Name=title, ChannelID=channelID, SKUName=None)
                if third_partys:
                    third_partyid = third_partys[0].ID
                    lesson_category_id = third_partys[0].LessonCategoryID
                        
                trade = TradeInfo(IsImported=1, UserID=user.ID, TradeID=trade_sn, ChannelID=channelID, Name=title, 
                         Payment=payment, Created=pay_time, PayTime=pay_time, SKUName=sku, ThirdPartyID=third_partyid, LessonCategoryID=lesson_category_id)
                trade.save()
        return HttpResponse("ok")                 
    except Exception,e:
        Log("UpdateUserAndTradesFromEdusoho error :%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    finally:
        connection.close()
        
def CreateTrade(mobile, username, tradeID, lessonName, channelID, fee, payType, sku='', oitm_id=''):
    try:
        tradeInfo = TradeInfo.objects.filter(TradeID = tradeID)
        if tradeInfo:
            return
        user = User.objects.filter(Mobile=mobile)

        if not user:
            area = GetUserAreaByMobile(mobile)
            province = ''
            city = ''
            user_zip = ''
            segmentName = ''
            if type(area) is dict:
                province = area.get('province', '')
                city = area.get('cityName', '')
                user_zip = area.get('postCode', '')
                segmentName = area.get('segmentName', '')
            user = User(IsImported=False, Name=username, NickName=username, Mobile=mobile, ChannelID=channelID, DistributorName=None, Province=province, 
                       City=city, Zip=user_zip, SegmentName=segmentName)
            user.save()
            #updateVar('User')
            #user = getVar('User').filter(Mobile=mobile)[0]
        else:
            user = user[0]
            user.NickName = username
            user.save()
        
        trade = TradeInfo(UserID=user.ID, IsImported=False, TradeID=tradeID, ChannelID=channelID, ProdCount=1, Name=lessonName, SKUName=sku,
                     PayType=payType, Created=datetime.datetime.now(), Updated=datetime.datetime.now(),
                     Payment=fee, DistributorName=None, DistributorType=None, Relations=None, OuterTradeID=oitm_id)
        trade.save()
        trade = TradeInfo.objects.filter(TradeID=tradeID)[0]
        #CreateDzhidianTradeNoadmin(trade)
        CreateDzhidianTradeAli(trade)
        trade.save()
        
        return True
    except Exception, e:
        Log("CreateTrade error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return False
    
def CreateDzhidianTradeNoadmin(trade):
        connection = pymysql.connect(**config)
        admin = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE nickname = 'admin' LIMIT 1")
                admin = cursor.fetchone()
        except Exception, e:
            Log("InsertEdusoho error:%s"%e, "local", "0.0.0.0", "DEBUG")
        finally:
            connection.close()
        
        imported = CreateDzhidianTrade(admin, trade)
        if imported != 'error':
            trade.IsImported = True
            trade.save()
        
def VerifyMobile(mobile):
    if len(str(mobile)) != 11:
        return False
    if str(mobile).startswith('1') == False:
        return False
    return True


def UpdateThirdParytID(request):
    try:
        #现阶段只考虑ChannelID = 1的
        channelID = 1
        Log("UpdateThirdParytID start", Type="DEBUG")
        trades = TradeInfo.objects.filter(ChannelID = 1, ThirdPartyID = None)
        res = []
        count = 0
        for trade in trades:
            sku = trade.SKUName
            third_partys = None
            if sku:
                third_partys = LessonsOfThirdParty.objects.filter(Name=trade.Name, ChannelID=channelID, SKUName=sku)
            else:
                third_partys = LessonsOfThirdParty.objects.filter(Name=trade.Name, ChannelID=channelID, SKUName=None)
            if third_partys:
                count += 1
                trade.ThirdPartyID = third_partys[0].ID
                trade.save()

        return HttpResponse(count)
    except Exception, e:
        Log("DeleteDupleOrder error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def UpdateThirdParytLessons(request):
    try:
        #大指新课程要统计
        channelID = 1
        Log("UpdateThirdParytLessons start", Type="DEBUG")
        lessons = Lesson.objects.all()
        count = 0
        for lesson in lessons:
            third_party = LessonsOfThirdParty.objects.filter(Name=lesson.Name, ChannelID=channelID, SKUName=lesson.TeachingPlan)
            if not third_party:
                third_party = LessonsOfThirdParty(Name=lesson.Name, ChannelID=channelID, SKUName=lesson.TeachingPlan, TelMsgTemplateID=0)
                third_party.save()
                count += 1

        return HttpResponse(count)
    except Exception, e:
        Log("UpdateThirdParytLessons error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    

def DeleteDupleOrder(request):
    try:
        Log("DeleteDupleOrder start", Type="DEBUG")
        trades = TradeInfo.objects.values("TradeID","Name","UserID", "SKUName").filter(ChannelID = 1, Payment = 0.0,TradeID__contains= 'EdusohoOrder20180804')
        res = []
        count = 0
        for trade in trades:
            t = TradeInfo.objects.values("TradeID").filter(ChannelID = 1, Name=trade['Name'], UserID=trade['UserID'], SKUName=trade['SKUName']).filter(~Q(TradeID=trade['TradeID']))
            if t:
                x = TradeInfo.objects.filter(ChannelID = 1, Name=trade['Name'], UserID=trade['UserID'], SKUName=trade['SKUName'], TradeID=trade['TradeID'], Payment = 0.0)
                x.delete()
                count += 1
                if x:
                    res.append({'tradeid': trade['TradeID'], "Name":trade['Name'], "UserID": trade['UserID']})
        #connection = pymysql.connect(**config)
        #connection.close()
        return HttpResponse("%d %s" % (count, json.dumps(res)))
    except Exception, e:
        Log("DeleteDupleOrder error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def UpdateLessonCategory(request):
    try:
        cates = LessonCategory.objects.values("ID","Name").all()
        cateDic = {}
        for cate in cates:
            cateDic[cate['Name']] = cate['ID']
        lessons = LessonsOfThirdParty.objects.filter(LessonCategoryID=0)
        name = ''
        for lesson in lessons:
            cate_id = 0
            name = lesson.Name.strip()
            cate = Cate1.objects.filter(YouzanName = name)
            if not cate:
                cate = Cate1.objects.filter(LessonName = name)
                if not cate:
                    cate = Cate2.objects.filter(YouzanName = name)
                    if not cate:
                        cate = Cate1.objects.filter(XiaoeName = name)
                        if not cate:
                            cate = Cate3.objects.filter(DazhiName = name)
            if cate:
                Log("FunctionTest xxx", "local", "0.0.0.0", "DEBUG")
                if cateDic.has_key(cate[0].Category):
                    cate_id = cateDic[cate[0].Category]
                else:
                    cate_id = 5
            lesson.LessonCategoryID = cate_id
            lesson.save()
            
        return HttpResponse(len(lessons))
    except Exception, e:
        Log("UpdateLessonCategory error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def UpdateTradeCategory(request):
    try:
        cates = LessonsOfThirdParty.objects.values("ID","LessonCategoryID").all()
        cateDic = {}
        for cate in cates:
            cateDic[cate['ID']] = cate['LessonCategoryID']
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID = None),LessonCategoryID=None)
        num = 0
        for trade in trades:
            cate_id = cateDic[trade.ThirdPartyID]
            trade.LessonCategoryID = cate_id
            trade.save()
            num += 1
            if num >= 5000:
                break;
        return HttpResponse(len(trades))
    except Exception, e:
        Log("UpdateTradeCategory error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

    

    
    
def import_test(request):
    try:
        connection2 = pymysql.connect(**config)
        return HttpResponse(1)
    except Exception, e:
        Log("import_test error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    

    
    
    