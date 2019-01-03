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
import import_views
import talk_cloud_views
import xlrd
import xlwt
import StringIO
import csv
import wxUtils
import point_views


        
def StudentPage(request):
    params = request.GET
    tagid = params.get('tagid')
    template = loader.get_template('students.html')
    context = RequestContext(request, {"Info":("ticket")})#{"students":getVar('User')})
    return HttpResponse(template.render(context))

def user_contract(request):
    params = request.GET
    template = loader.get_template('user_contract.html')
    context = RequestContext(request, {"Info":("ticket")})#{"students":getVar('User')})
    return HttpResponse(template.render(context))  
    
def StudentList(request):
    params = request.GET
    try:
        offset=0
        limit=10
        start=None
        end=None
        Log("StudentList params: %s" % params, "local", "0.0.0.0", "DEBUG")
        
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        
        users = getStudents(params)
        
        page = int(offset/limit + 1)
        Log("StudentList page: %d" % page, "local", "0.0.0.0", "DEBUG")
        
        total = len(users)
        res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        channelDic = GetChannelRemarkDic()
        
        trades = TradeInfo.objects.values("ID","UserID","Payment","IsRefund","PayTime").filter(~Q(ThirdPartyID=None))
        wx_usres = wxUser.objects.values("ID","Mobile")
        associated_mobiles = []
        for wx_user in wx_usres:
            associated_mobiles.append(wx_user['Mobile'])
        while i < last:
            user = users[i]
            channelRemark = channelDic[user.ChannelID]
            wx_user = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5',Mobile=user.Mobile)
            associated = "否"
            if user.Mobile in associated_mobiles:
                associated = "是"
            user_trades = []
            for trade in trades:
                if trade['UserID'] == user.ID:
                    user_trades.append(trade)
            #user_trades = TradeInfo.objects.filter(UserID = user.ID).filter(~Q(ThirdPartyID=None))
            count = len(user_trades)
            last_trade = ''
            if count >0:
                last_trade = user_trades[count-1]['PayTime'].strftime("%Y-%m-%d %H:%M:%S")
            fee = 0
            for user_trade in user_trades:
                if not user_trade['IsRefund']:
                    fee += user_trade['Payment']
            #user_campaign = UserCampaign.objects.filter(User)
            detail = "<a href='javascript:showdetail(%d)'>详细信息</a>" % user.ID
            res.append({"ID":user.ID, 'Name': user.Name, 'Mobile': user.Mobile, "ChannelName":channelRemark, "Distributor":user.DistributorName, "Associated":associated, "ChildAge":user.ChildAge, 
                        'Created': user.Created.strftime("%Y-%m-%d %H:%M:%S"), "Province":user.Province, "Count":count, "Detail": detail, "Payment": str(fee), 'NickName': user.NickName, 
                        "ChildName":user.ChildName, "WechatCode":user.WechatCode, "last_trade":last_trade})
            i=i+1
        
        #获得用户群的openid
        mobiles = [user.Mobile for user in users]
        openids = wxUser.objects.values('openID').filter(Mobile__in=mobiles)
        open_ids = [openid['openID'] for openid in openids]
        
        #Log("StudentList openids: %s" % open_ids, "local", "0.0.0.0", "DEBUG")
        obj = {
            "page":page,
            "rows":res,
            "total":total,
            "openids":open_ids
        }
        #Log("StudentList obj: %s" % obj, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("StudentList error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')
    
    
@csrf_exempt
def UploadStudent(request):
    try:
        params = request.POST
        if request.FILES.has_key("student_file"):
            channel_id = int(params.get("upload_channel"))
            student_file = request.FILES["student_file"]
            #csv_reader = csv.reader(classes_file)
            data = xlrd.open_workbook(file_contents=student_file.read())
            table = data.sheets()[0]
            nrows = table.nrows
            line_num = 0
            for i in range(nrows ):
                row = table.row_values(i)
            #for row in csv_reader:
                if line_num == 0:
                    if str(row[0].strip()) != u"学生姓名" or row[1].strip() != u"电话":
                        return HttpResponse('列名不对，请确认是否传错文件')
                if line_num > 0:
                    student_name = row[0].strip()
                    #姓名为空不导入
                    if not student_name:
                        continue
                    #电话无效不导入
                    mobile = 0
                    try:
                        mobile = int(row[1])
                    except Exception,e:
                        mobile = 0
                    if mobile == 0:
                        continue;
                    #已有学员只修改姓名
                    student = User.objects.filter(Mobile=mobile)
                    if student:
                        student[0].ChildName = student_name
                        student[0].save()
                    else:
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
                        student = User(Mobile=mobile, Name=student_name, ChildName=student_name, ChannelID=channel_id, Role=0, DistributorName=None, NickName=None, Province=province, 
                                       City=city, Zip=user_zip, SegmentName=segmentName)
                        student.save()

                    #Log("UploadClasses row %s" % row, Type="DEBUG")
                line_num += 1
        
        #CloudClass.objects.filter(CloudCourseID = course_id).delete()
        #CloudCourseMember.objects.filter(CloudCourseID=course_id).update(CloudClassID = None)
        
            return HttpResponse('ok')
        else:
            return HttpResponse('没找到文件')
    except Exception,e:
        Log("UploadStudent error: %s" %e, Type="DEBUG")
        return HttpResponse(e)    
    
    
def ExportStudents(request):
    params = request.GET
    try:
        Log("ExportStudents params: %s" % params, "local", "0.0.0.0", "DEBUG")
        users = getStudents(params)#.values("ID","Name","Mobile","ChannelID","DistributorName","Created",)
        channelDic = GetChannelRemarkDic()
        
        response = HttpResponse(mimetype="text/csv; charset=gb2312")
        response['Content-Disposition'] = 'attachment; filename=students.csv'
        writer = csv.writer(response, dialect='excel')
        writer.writerow(["编号".encode('gb2312','ignore'),"姓名".encode('gb2312','ignore'),"电话".encode('gb2312','ignore'),"课程数".encode('gb2312','ignore'),"金额".encode('gb2312','ignore'),"来源渠道".encode('gb2312','ignore'),"分销商".encode('gb2312','ignore')
                             ,"绑定服务号".encode('gb2312','ignore'),"注册时间".encode('gb2312','ignore'),"地区".encode('gb2312','ignore'),"微信昵称".encode('gb2312','ignore'),"孩子姓名".encode('gb2312','ignore'),"孩子年龄".encode('gb2312','ignore')])
        
        trades = TradeInfo.objects.values("ID","UserID","Payment").filter(~Q(ThirdPartyID=None))
        wx_usres = wxUser.objects.values("ID","Mobile")
        associated_mobiles = []
        for wx_user in wx_usres:
            associated_mobiles.append(wx_user['Mobile'])
        
        for user in users:
            channelRemark = channelDic[user.ChannelID]
            #wx_user = wxUser.objects.values("ID","Mobile").filter(Mobile=user.Mobile)
            associated = "否"
            if user.Mobile in associated_mobiles:
                associated = "是"

            user_trades = []
            for trade in trades:
                if trade['UserID'] == user.ID:
                    user_trades.append(trade)
            #user_trades = trades.filter(UserID = user.ID)
            count = len(user_trades)
            fee = 0
            for user_trade in user_trades:
                fee += user_trade['Payment']
            distributor = ''
            if user.DistributorName:
                distributor = user.DistributorName
            province = ''
            if user.Province:
                province = user.Province
            nickname = ''
            if user.NickName:
                nickname = user.NickName
            childname = ''
            if user.ChildName:
                childname = user.ChildName
            writer.writerow([user.ID,user.Name.encode('gb2312','ignore'),user.Mobile,count,str(fee),channelRemark.encode('gb2312','ignore'),distributor.encode('gb2312','ignore')
                             ,associated.encode('gb2312','ignore'),user.Created.strftime("%Y-%m-%d %H:%M:%S"),province.encode('gb2312','ignore'), nickname.encode('gb2312','ignore'),childname.encode('gb2312','ignore'),user.ChildAge])
        return response
    except Exception, e:
        Log("ExportStudents error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
def getStudents(params):
        users = User.objects.filter(Role=0).order_by("-Created")
        
        trades = TradeInfo.objects.filter(~Q(ThirdPartyID=None))
        if params.has_key('mobile'):
            mobile = params['mobile']
            try:
                mobile = str(mobile)
                if len(mobile) >= 4:
                    users = users.filter(Mobile__contains=mobile)
            except Exception,e:
                mobile = ''
        if params.has_key('channel'):
            channel=params['channel']
            if channel and channel != 'all':
                try:
                    channel=int(channel)
                    users = users.filter(ChannelID=channel)
                except Exception,e:
                    channel=str(channel)
                    users = users.filter(DistributorName=channel)
        if params.has_key('is_new'):
            is_new=params['is_new']
            try:
                userIDs = None
                ids = []
                userIDs = trades.values("UserID").filter(IsNewUserTrade=int(is_new))
                if userIDs is not None:
                    for userID in userIDs:
                        ids.append(userID['UserID'])
                    users = users.filter(ID__in=ids)
            except Exception,e:
                is_new = None
        if params.has_key('lesson_id[]'):
            lesson_id=params.getlist('lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                userIDs = trades.filter(ThirdPartyID__in=lesson_ids).values("UserID").distinct()
                ids = []
                for userID in userIDs:
                    ids.append(userID['UserID'])
                users = users.filter(ID__in=ids)
            except Exception,e:
                lesson_id = None
        elif params.has_key('lesson_ids'):
            lesson_id=params.get('lesson_ids')
            try:
                lesson_ids=lesson_id.split(',')
                userIDs = trades.filter(ThirdPartyID__in=lesson_ids).values("UserID").distinct()
                ids = []
                for userID in userIDs:
                    ids.append(userID['UserID'])
                users = users.filter(ID__in=ids)
            except Exception,e:
                lesson_id = None
        #else:
        #        #必须是有效课程才算学员,现在加上campaign用户
        #        userIDs = trades.values("UserID").distinct()
        #        ids = []
        #        for userID in userIDs:
        #            ids.append(userID['UserID'])
        #        users = users.filter(Q(ID__in=ids) | Q(~Q(Campaign=None), ~Q(Campaign='')))
        if params.has_key('non_lesson_id[]'):
            lesson_id=params.getlist('non_lesson_id[]')
            try:
                lesson_ids=[int(lesson) for lesson in lesson_id]
                userIDs = trades.filter(ThirdPartyID__in=lesson_ids).values("UserID").distinct()
                ids = []
                for userID in userIDs:
                    ids.append(userID['UserID'])
                users = users.filter(~Q(ID__in=ids))
            except Exception,e:
                non_lesson_id = None
        elif params.has_key('non_lesson_ids'):
            lesson_id=params.get('non_lesson_ids')
            try:
                lesson_ids=lesson_id.split(',')
                userIDs = trades.filter(ThirdPartyID__in=lesson_ids).values("UserID").distinct()
                ids = []
                for userID in userIDs:
                    ids.append(userID['UserID'])
                users = users.filter(~Q(ID__in=ids))
            except Exception,e:
                non_lesson_id = None
        if params.has_key('lesson_count'):
            lesson_count=params['lesson_count']
            try:
                if len(lesson_count.split('_')) > 1:
                    s = lesson_count.split('_')
                    oper = s[0]

                    userIDs = trades.values("UserID").annotate(dcount=Count("UserID"))
                    ids = []
                    not_ids = []
                    for userID in userIDs:
                        if oper == "eq":
                            c = int(s[1])
                            if c == 0:
                                not_ids.append(userID['UserID'])
                            elif userID['dcount'] == c:
                                ids.append(userID['UserID'])
                        if oper == "bt":
                            c_s = s[1].split(',')
                            c0 = int(c_s[0])
                            c1 = int(c_s[1])
                            if userID['dcount'] >= c0 and userID['dcount'] <= c1:
                                ids.append(userID['UserID'])
                        if oper == "lt":
                            c = int(s[1])
                            if userID['dcount'] <= c:
                                ids.append(userID['UserID'])
                        if oper == "gt":
                            c = int(s[1])
                            if userID['dcount'] >= c:
                                ids.append(userID['UserID'])
                    if ids:
                        users = users.filter(ID__in=ids)
                    elif not_ids:
                        users = users.filter(~Q(ID__in=not_ids))
            except Exception,e:
                lesson_count = None
        if params.has_key('associated'):
            associated=params['associated']
            try:
                associated = int(associated)
                wx_user = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5',MobileBound=1)
                mobiles = []
                for u in wx_user:
                    mobiles.append(u.Mobile)
                if associated == 1:
                    users = users.filter(Mobile__in=mobiles)
                elif associated == 0:
                    users = users.filter(~Q(Mobile__in=mobiles))
            except Exception,e:
                associated = None
        if params.has_key('startDate'):
            start=params['startDate']
            try:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                users = users.filter(Created__gt=start)
            except Exception,e:
                start = None
        if params.has_key('endDate'):
            end=params['endDate']
            try:
                end = datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(days = 1)
                users = users.filter(Created__lt=end)
            except Exception,e:
                end = None
        if params.has_key('tag_ids'):
            tag_ids=params['tag_ids']
            try:
                if tag_ids:
                    tags = tag_ids.split(',')
                    tags = [int(x) for x in tags]
                    users_temp = []
                    for user in users:
                        if not user.TagIDs:
                            continue
                        user_tags = user.TagIDs.split(',')
                        for tag in user_tags:
                            if int(tag) in tags:
                                users_temp.append(user)
                                break
                    users = users_temp
            except Exception,e:
                tag_ids = None
        return users

    
def StudentDetail(request):
    try:
        params = request.GET
        Log("StudentDetail params: %s" % params, "local", "0.0.0.0", "DEBUG")
        user_id=params.get('userId');
        user = User.objects.get(ID=user_id)

        channelDic = GetChannelRemarkDic()
        channelRemark = channelDic[user.ChannelID]
        userTags = []
        if user.TagIDs:
            tags = user.TagIDs.split(',')
            arrInt = [int(x) for x in tags]
            if tags:
                for tag in getVar('UserTag'):
                    if tag.ID in arrInt:
                        userTags.append({"ID":tag.ID, "Name":tag.Name, "Description": tag.Description})
            
        res = {"ID":user.ID, "Name":user.Name, "ChannelName":channelRemark, "Mobile":user.Mobile, "Distributor": user.DistributorName, "Created": user.Created.strftime("%Y-%m-%d %H:%M:%S"), "tags": userTags, "Province": user.Province}
        #Log("StudentList obj: %s" % obj, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("StudentDetail error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')
    
def StudentTrade(request):
    try:
        params = request.GET
        offset=0
        limit=10
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        user_id=params.get('userId');
        Log("StudentTrade params: %s" % params, "local", "0.0.0.0", "DEBUG")
        trades=TradeInfo.objects.filter(UserID = user_id).filter(~Q(ThirdPartyID=None))        
        page = int(offset/limit + 1)
        
        total = len(trades)
        res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        channelDic = GetChannelRemarkDic()
        while i < last:
            trade = trades[i]
            channelRemark = channelDic[trade.ChannelID]
            imported = "否"
            if trade.ThirdPartyID is not None:
                imported = "是"
            edit = ''
            if trade.ChannelID == 15:
                if trade.IsRefund == 1:
                    edit = '已退款'
                else:
                    edit = "<a href='javascript:trade_refund(%d)'>退款</a>&nbsp;" % int(trade.ID)
            trade_obj = {"ID":trade.ID, 'TradeID': trade.TradeID, "Name": trade.Name ,'ChannelName':channelRemark, 'Distributor':trade.DistributorName, 
                        'Imported':imported, "Payment": str(trade.Payment), 'PayTime':trade.PayTime.strftime("%Y-%m-%d %H:%M:%S"), 'TimeStamp':trade.TimeStamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'Edit':edit}
            res.append(trade_obj)
            i=i+1
        #Log("StudentList res: %s" % res, "local", "0.0.0.0", "DEBUG")
        obj = {
            "page":page,
            "rows":res,
            "total":total
        }
        #Log("StudentList obj: %s" % obj, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("StudentTrade error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')

def SendVerificationCode(request):
    try:
        key=random_verificaioncode()
        content="【外滩教育】您的验证码是%d，有效期是10分钟，请尽快输入。" % key
        if request.method == "GET":
            params = request.GET
            mobile = params['mobile']
            openid = params['openid']
            appid = params['appid']
            blacklist = ['oxHGE1K5FUjEj6VrB_BaTf8ENwL0','oxHGE1Bhch256Nprpbk_355Uh0zQ']
            #Log("SendVerificationCode openid %s %s"%(openid,mobile), "local", "0.0.0.0", "DEBUG")
            if openid in blacklist:
                #time.sleep(5)
                #Log("SendVerificationCode blacklist openid %s %s"%(openid,mobile), "local", "0.0.0.0", "DEBUG")
                #Log("SendVerificationCode ip %s"% request.META.get("REMOTE_ADDR",None), "local", "0.0.0.0", "DEBUG")
                return HttpResponse("玩的开心")
            
            users = wxUser.objects.filter(openID = openid)
            
            if not users:
                Log("SendVerificationCode invalid openid %s %s"%(openid,mobile), "local", "0.0.0.0", "DEBUG")
                return HttpResponse("openid 不合法")
            
            userInfo = users[0]
            userInfo = users[0]
            userInfo.VerificationCode = key
            userInfo.Mobile = mobile
            userInfo.VerificationCodeExpired = datetime.datetime.now() + datetime.timedelta(minutes = 10)
            userInfo.DailySendTimes += 1
            userInfo.save()
            if userInfo.DailySendTimes <= 5:
                res = Send106txtTelMsg(mobile,content)
                if res != '1':
                    return HttpResponse(res)
            else:
                Log("SendVerificationCode openid %s %s"%(openid,mobile), "local", "0.0.0.0", "DEBUG")
                return HttpResponse("每天最多请求5次，如有需要，请联系客服。")
            
            return HttpResponse(res)
        else:
            return HttpResponse("no params get")
    except Exception, e:
        Log("SendVerificationCode error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

@csrf_exempt
def SetCampaignUser(request):
    try:
        params = request.POST
        mobile = params.get('mobile')
        username = params.get('username')
        age = int(params.get('age'))
        campaign = params.get('campaign')
        user = User.objects.filter(Mobile=mobile)
        channel = getVar('Channel').values('ID').filter(Name='campaign')[0]
        campaign = getVar('Campaign').values('ID').filter(Code=campaign)[0]
        if user:
            #user[0].Campaign = campaign
            user[0].ChildName = username
            user[0].ChildAge = age
            user[0].save()
            user_campaign = UserCampaign.objects.filter(UserID=user[0].ID, CampaignID=campaign['ID'])
            if not user_campaign:
                user_campaign = UserCampaign(UserID=user[0].ID, CampaignID=campaign['ID'])
                user_campaign.save()
        else:
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
            user = User(Mobile=mobile, ChildName=username, ChannelID = channel['ID'], ChildAge=age, Province=province, 
                       City=city, Zip=user_zip, SegmentName=segmentName)
            user.save()
            
            user_campaign = UserCampaign(UserID=user.ID, CampaignID=campaign['ID'])
            user_campaign.save()
        return HttpResponse('ok')
    except Exception,e:
        Log('SetCampaignUser Error: %s' % e, Type="DEBUG")
        return HttpResponse(e)    
    
@csrf_exempt
def VerifyCode(request):
    try:
        res = "绑定失败"
        if request.method == "POST":
            params = request.POST
            Log("VerifyCode %s" %params, "local", "0.0.0.0", "DEBUG")
            mobile = params['mobile']
            openid = params['openid']
            if not openid:
                return HttpResponse('无效的OpenID')
            code = params['code']
            users = wxUser.objects.filter(openID = openid)
            userInfo = users[0]
            if datetime.datetime.now() > userInfo.VerificationCodeExpired:
                res="验证码超时，请重新申请"
            else:
                if userInfo.VerificationCode == int(code):
                    if userInfo.Mobile == mobile:
                        res = "ok"
                        userInfo.Mobile = mobile
                        userInfo.MobileBound = True
                        userInfo.save()
                        #绑定导入课程，暂停11-7
                        curr_time=time.time()
                        time_local = time.localtime(curr_time)
                        sn = time.strftime("%Y%m%d%H%M%S",time_local) + str(datetime.datetime.now().microsecond)
                        lesson = LessonsOfThirdParty.objects.get(ID = 92)
                        import_views.CreateTrade(mobile, userInfo.Name, 'USERBIND%s' % sn, lesson.Name, lesson.ChannelID, 0, "Free")
                    else:
                        res = "输入的手机号与获得验证码的号码不同，请重新输入"
                else:
                    res = "验证码错误"
        return HttpResponse(res)
    except Exception, e:
        Log("SendVerificationCode error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def ClearDailySendTimes(request):
    wxUser.objects.update(DailySendTimes=0)
    return HttpResponse('ok')
    
def GetProvince(request):
    try:
        params = request.GET
        Log("GetProvince params: %s" % params, "local", "0.0.0.0", "DEBUG")
        
        provinces = User.objects.distinct().values("Province")
        res = []
        for province in provinces:
            res.append(province['Province'])

        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetProvince error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse('')
    

def CheckDownloadUser(request):
    try:
        download_user = ['ob3OJ1ty-6Og_D8j_JXe6fEub0MU','ob3OJ1g2XlwWcdv4mZVHAkbz0YqY','ob3OJ1gIbfmEmP9mMyffhoisb1BQ']
        params = request.GET
        #Log("CheckDownloadUser params: %s" % params, "local", "0.0.0.0", "DEBUG")
        unionid = params.get('unionid', None)
        #Log("CheckDownloadUser unionid: %s" % unionid, "local", "0.0.0.0", "DEBUG")
        if unionid in download_user:
            return HttpResponse(1)
        return HttpResponse(0)

    except Exception,e:
        Log("CheckDownloadUser error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(0)
    

@csrf_exempt
def TradeRefund(request):
    try:        
        params = request.POST
        Log("BillRefund params: %s" % params, Type="DEBUG")
        trade_id = params.get('trade_id', 0)
        trade = TradeInfo.objects.filter(ID=trade_id)
        res = ''
        if trade:
            trade = trade[0]
            if trade.ChannelID == 15:
                res = wxUtils.OrderRefund(int(trade.OuterTradeID))
                if res == 'success':
                    trade.IsRefund = 1
                    trade.save()
                    points = UserPointDetail.objects.filter(ObjectType="OITM",ObjectID=trade.OuterTradeID)
                    for point in points:
                        if point.Points > 0:
                            point_views.UpdatePointToUser(point.wxUserID, -point.Points, object_type='OITM', object_id=trade.OuterTradeID, reason="退款") 
        else:
            return HttpResponse('no trade found')
        
        return HttpResponse(res)
    except Exception,e:
        Log("BillRefund error: %s" %e, Type="DEBUG")
        return HttpResponse(e)

    

    
