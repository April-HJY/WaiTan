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
import talk_cloud_interface

        
def talk_cloud_login(request):
        code = random_str(20)
        template = loader.get_template('talk_cloud_login.html')
        context = RequestContext(request, {"Info":mc.get("ticket"),'action_code':code})
        return HttpResponse(template.render(context))
    
def talk_cloud_courses(request):
        code = random_str(20)
        template = loader.get_template('talk_cloud_courses.html')
        context = RequestContext(request, {"Info":mc.get("ticket"),'action_code':code})
        return HttpResponse(template.render(context))

def talk_cloud_create_class(request):
    try:
        course_id = 1
        class_id = 1
        name = '测试课'
        chairmanpwd = random_verificaioncode(4)
        assistantpwd = random_verificaioncode(4)
        patrolpwd = random_verificaioncode(4)
        confuserpwd = random_verificaioncode(4)
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now() + timedelta(minutes = 5)
        room_type = 0
        res = talk_cloud_interface.CreateClass(name, chairmanpwd, assistantpwd, patrolpwd, confuserpwd, start_time, end_time)
        if not res:
            return HttpResponse("创建失败，请查看日志")
        class_room = CloudClassRoom(CloudLessonCourseID=course_id, CloudClassID=class_id, Name=name, Serial=res['serial'], Version=res['version'], StartTime=start_time, EndTime=end_time, 
                                    TeacherPwd=chairmanpwd, PatrolPwd=patrolpwd, AssistantPwd=assistantpwd, StudentPwd=confuserpwd)
        class_room.save()
        return HttpResponse('ok')
    except Exception,e:
        Log("talk_cloud_create_class error: %s" %e, Type="DEBUG")
        return HttpResponse(e)

    
    
def GetUserInfo(request):
    try:
            Log("GetUserInfo start", "local", "0.0.0.0", "DEBUG")
            params = request.GET
            mobile = params['mobile']
            user = User.objects.get(Mobile=mobile)
            wxuser = wxUser.objects.get(Mobile=mobile, SourceAccount="wx457b9d0e6f93d1c5")
            if not user or not wxuser:
                return HttpResponse(None)
            name = user.Name
            if not name or name == ' ':
                name = wxuser.Name
            avatar = wxuser.Avatar
            if not avatar:
                avatar = '../static/images/pic_touxiang.png'
            res = {"Name":name, "Avatar":avatar}
            
            return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetUserInfo error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(None)
    
@csrf_exempt
def LoginVerifyCode(request):
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
                        #绑定导入课程
                        
                    else:
                        res = "输入的手机号与获得验证码的号码不同，请重新输入"
                else:
                    res = "验证码错误"
        return HttpResponse(res)
    except Exception, e:
        Log("SendVerificationCode error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetScanUser(request):
    try:
        params = request.GET
        code = params.get('code')
        #Log("GetScanUser code:%s"%code, Type="DEBUG")
        appid = "wx457b9d0e6f93d1c5";
        user = wxUser.objects.filter(QRCodeTicket=code)
        res = None
        if user:
            name = ''
            u = User.objects.filter(Mobile=user[0].Mobile)
            if u and u[0].Name.strip():
                name = u[0].Name
            else:
                name = user[0].Name
            #url = talk_cloud_classroom_url(user[0].Name)
            res = {"ID":user[0].ID, "Name":name, "OpenID":user[0].openID, "QRCodeTicket":user[0].QRCodeTicket, "SourceAccount":user[0].SourceAccount, 
                   "MobileBound": user[0].MobileBound, "Mobile": user[0].Mobile}
        else:
            time.sleep(1)
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetScanUser error: %s" % e, Type="DEBUG")
        return HttpResponse(None)
    
    
def GetQRCode(request):
    try:
        params = request.GET
        code = params.get('code')
        appid = "wx457b9d0e6f93d1c5";
        #Log("GetQRCode code:%s"%code, "local", "0.0.0.0", "DEBUG")
        wxObj = wxAccountInterface.wxAccountInterface(appid)
        res = wxObj.GetQRCode(code)
        return HttpResponse(res)
    except Exception,e:
        Log("GetQRCode error: %s" % e, Type="DEBUG")
        return HttpResponse(None)
    
    
def GetUserLessons(request):
    try:
        params = request.GET
        Log("GetUserLessons params: %s" %params, Type="DEBUG")
        mobile = params.get("mobile", 0)
        user = User.objects.values("ID").get(Mobile=mobile)
        user_id = user['ID']
        course_members = CloudCourseMember.objects.values("CloudCourseID","CloudClassID","Role","Name").filter(UserID=user_id, IsHide = 0)
        class_ids = []
        course_ids = []
        for course_member in course_members:
            class_ids.append(course_member['CloudClassID'])
            course_ids.append(course_member['CloudCourseID'])
        courses = CloudCourse.objects.values("ID", "Name", "SKUValue1", "SKUValue2", "SKUValue3", "SKUValue4").filter(ID__in=course_ids)
        lessons = CloudCourseLesson.objects.values("ID", "Name", "StartTime", "CloudCourseID").filter(CloudCourseID__in=course_ids).order_by("CloudCourseID", "StartTime")
        class_rooms = CloudClassRoom.objects.values("ID","CloudCourseID","Name","Serial","TeacherPwd","StudentPwd","CloudCourseLessonID","StartTime").filter(CloudClassID__in=class_ids)
        wxuser = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5',Mobile=mobile)
        nick_name = ''
        if wxuser:
            nick_name = wxuser[0].Name
        res = []
        for lesson in lessons:
            
            lesson['serial'] = 0
            lesson['teacher_pwd'] = ''
            lesson['student_pwd'] = ''
            lesson['role'] = 0
            lesson['course_name'] = ''
            lesson['button'] = '<input type="button" class="button-disabled" disabled=disabled value="未开始"/>'
            for course in courses:
                sku = ''
                if course['ID'] == lesson['CloudCourseID']:
                    if course['SKUValue1']:
                        sku += " %s" % course['SKUValue1']
                    if course['SKUValue2']:
                        sku += " %s" % course['SKUValue2']
                    if course['SKUValue3']:
                        sku += " %s" % course['SKUValue3']
                    if course['SKUValue4']:
                        sku += " %s" % course['SKUValue4']
                    lesson['course_name'] = course['Name']
                    if sku:
                        lesson['course_name'] += sku
                    break;
            for class_room in class_rooms:
                if lesson['ID'] == class_room['CloudCourseLessonID']:
                    lesson['serial'] = class_room['Serial']
                    lesson['teacher_pwd'] = class_room['TeacherPwd']
                    lesson['student_pwd'] = class_room['StudentPwd']
                    lesson['classroom_name'] = class_room['Name']
                    lesson['classroom_starttime'] = class_room['StartTime']
                    #Log("GetUserLessons starttime: %s" %lesson['classroom_starttime'], Type="DEBUG")
                    break
            for course_member in course_members:
                if lesson['CloudCourseID'] == course_member['CloudCourseID']:
                    lesson['role'] = course_member['Role']
                    lesson['student_name'] = course_member['Name']
                    break
            if not lesson['student_name'] or lesson['student_name'] == ' ':
                lesson['student_name'] = nick_name
            if not lesson['student_name']:
                lesson['student_name'] = '外滩学员'
            if lesson['serial'] > 0 and lesson['classroom_starttime'] < datetime.datetime.now():
                url = ''
                #Log("GetUserLessons student_pwd: %s" %lesson['student_pwd'], Type="DEBUG")
                #学生提前半小时才能进教室，老师教室创建了就能进
                if lesson['role'] == 0:
                    if lesson['StartTime'] + timedelta(minutes = -30) < datetime.datetime.now() and lesson['StartTime'] + timedelta(minutes = 120) > datetime.datetime.now():
                        url = talk_cloud_interface.GetClassroomURL(lesson['serial'],lesson['student_name'],2,time.time(),lesson['student_pwd'])
                        lesson['button'] = '<input type="button" class="button-enabled" onclick="start_class(\'%s\')" value="开始上课"/>' % url
                else:
                    url = talk_cloud_interface.GetClassroomURL(lesson['serial'],lesson['student_name'],0,time.time(),lesson['teacher_pwd'])
                    lesson['button'] = '<input type="button" class="button-enabled" onclick="start_class(\'%s\')" value="开始上课"/>' % url
                #Log("GetUserLessons url: %s" %url, Type="DEBUG")
                
            if lesson['StartTime'] + timedelta(minutes = 120) < datetime.datetime.now():
                lesson['button'] = '<input type="button" class="button-disabled" disabled=disabled value="已结束"/>'
            lesson['StartTime'] = lesson['StartTime'].strftime("%Y-%m-%d %H:%M")
            if lesson.has_key('classroom_starttime'):
                lesson['classroom_starttime']=lesson['classroom_starttime'].strftime("%Y-%m-%d %H:%M")
            res.append(lesson)
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetUserLessons error: %s" %e, Type="DEBUG")
        return HttpResponse(json.dumps([]))

    
    