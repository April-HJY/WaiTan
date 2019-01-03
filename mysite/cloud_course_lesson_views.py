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
import talk_cloud_interface
import wxAccountInterface
import xlrd
import xlwt
import StringIO
import pymysql

def CourseSchedulePage(request):
    template = loader.get_template('courseschedulepage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))



def GetCloudCourses(request):
    try:
        updateVar('CloudCourse')
        courses = getVar('CloudCourse')
        params = request.GET
        offset=0
        limit=10
        if params.has_key('offset'):
            offset=int(params['offset'])
        if params.has_key('limit'):
            limit=int(params['limit'])
        page = int(offset/limit + 1)
        res = []
        for course in courses:
            if not course.Scheduled:
                edit = "<a href='javascript:popShow(%d)'>排课</a>" % (course.ID)
            else:
                edit = "<a href='javascript:popShow(%d)'>查看或修改</a>" % (course.ID)
            sku = "%s %s %s %s" % (course.SKUValue1 if course.SKUValue1 else '', course.SKUValue2 if course.SKUValue2 else '', course.SKUValue3 if course.SKUValue3 else '', course.SKUValue4 if course.SKUValue4 else '')
            res.append({"ID":course.ID, "Name":course.Name, "SKU": sku, "Edit": edit})
        total = len(res)
        x_res = []
        i = offset
        last = limit * page
        if last > total:
            last = total
        while i < last:
            x_res.append(res[i])
            i=i+1
            
        obj = {
            "page":page,
            "rows":x_res,
            "total":total,
        }
        #Log("GetAllCoupons obj %s" % obj, Type='DEBUG')
        return HttpResponse(json.dumps(obj))
    except Exception,e:
        Log("GetCloudCourses error: %s" %e, Type="DEBUG")
        return []
    

    
    
@csrf_exempt
def UploadCourse(request):
    try:
        #Log("UploadCourse", Type="DEBUG")
        params = request.POST
        if request.FILES.has_key("course_file"):
            #Log("UploadCourse1", Type="DEBUG")
            teacheres_file = request.FILES["course_file"]
            #csv_reader = csv.reader(classes_file)
            data = xlrd.open_workbook(file_contents=teacheres_file.read())
            table = data.sheets()[0]
            nrows = table.nrows
            line_num = 0
            for i in range(nrows ):
                row = table.row_values(i)
            #for row in csv_reader:
                if line_num == 0:
                    if (str(row[0].strip()) != u"课程名称" or row[1].strip() != u"SKUName1" or row[2].strip() != u"SKUValue1" or row[3].strip() != u"SKUName2" or row[4].strip() != u"SKUValue2"
                        or row[5].strip() != u"SKUName3" or row[6].strip() != u"SKUValue3" or row[7].strip() != u"SKUName4" or row[8].strip() != u"SKUValue4"):
                        return HttpResponse('列名不对，请确认是否传错文件')
                if line_num > 0:
                    course_name = row[0].strip()
                    #课程名为空不导入
                    if not course_name:
                        continue
                    skuname1 = None
                    skuvalue1 = None
                    if row[1].strip():
                        skuname1 = row[1].strip()
                        skuvalue1 = row[2].strip()
                        
                    skuname2 = None
                    skuvalue2 = None
                    if row[3].strip():
                        skuname2 = row[3].strip()
                        skuvalue2 = row[4].strip()
                        
                    skuname3 = None
                    skuvalue3 = None
                    if row[5].strip():
                        skuname2 = row[5].strip()
                        skuvalue2 = row[6].strip()
                        
                    skuname4 = None
                    skuvalue4 = None
                    if row[7].strip():
                        skuname2 = row[7].strip()
                        skuvalue2 = row[8].strip()
                    lesson_category_id=5
                    dic = GetCategoryNameDic
                    try:
                        if row[9].strip():
                            lesson_category_id = dic[row[9].strip()]
                    except Exception,e:
                        lesson_category_id = 5
                    #:;
                    course = CloudCourse.objects.filter(Name=course_name, SKUName1=skuname1, SKUValue1=skuvalue1, SKUName2=skuname2, SKUValue2=skuvalue2, 
                                                        SKUName3=skuname3, SKUValue3=skuvalue3, SKUName4=skuname4, SKUValue4=skuvalue4)
                    #Log("UploadCourse course: %s" %course, Type="DEBUG")
                    #已有课程不再添加
                    if not course:
                        course = CloudCourse(Name=course_name, SKUName1=skuname1, SKUValue1=skuvalue1, SKUName2=skuname2, SKUValue2=skuvalue2, 
                                                        SKUName3=skuname3, SKUValue3=skuvalue3, SKUName4=skuname4, SKUValue4=skuvalue4)
                        course.save()
                        sku_name = '';
                        if skuname1:
                            sku_name="%s:%s" %(skuname1,skuvalue1)
                        if skuname2:
                            sku_name+=";%s:%s" %(skuname2,skuvalue2)
                        if skuname3:
                            sku_name+=";%s:%s" %(skuname3,skuvalue3)
                        if skuname4:
                            sku_name+=";%s:%s" %(skuname4,skuvalue4)
                        if sku_name == '':
                            sku_name = None
                        third_party_lesson = LessonsOfThirdParty.objects.filter(Name=course_name, SKUName=sku_name, ChannelID=2)
                        #Log("UploadCourse third_party_lesson: %s" %third_party_lesson, Type="DEBUG")
                        #课程默认是有赞
                        if not third_party_lesson:
                            third_party_lesson = LessonsOfThirdParty(Name=course_name, SKUName=sku_name, ChannelID=2, LessonCategoryID=lesson_category_id)
                            third_party_lesson.save()
                        else:
                            third_party_lesson = third_party_lesson[0]
                            
                        UpdateCourseMember(course.ID, third_party_lesson.ID, course_name, sku_name, third_party_lesson.LessonCategoryID)
                    
                line_num += 1
        
        #CloudClass.objects.filter(CloudCourseID = course_id).delete()
        #CloudCourseMember.objects.filter(CloudCourseID=course_id).update(CloudClassID = None)
        
            return HttpResponse('ok')
        else:
            return HttpResponse('没找到文件')
    except Exception,e:
        Log("UploadCourse error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
def UpdateCourseMemberByDate(request):
    try:
        params = request.GET
        Log("UpdateCourseMemberByDate params: %s" % params, Type="DEBUG")
        course_id = int(params.get('id',0))
        course_date = params.get('date','2018-10-10')
        course = CloudCourse.objects.get(ID=course_id)

        sku_name = '';
        if course.SKUName1:
            sku_name="%s:%s" %(course.SKUName1,course.SKUValue1)
        if course.SKUName2:
            sku_name="%s:%s" %(course.SKUName2,course.SKUValue2)
        if course.SKUName3:
            sku_name="%s:%s" %(course.SKUName3,course.SKUValue3)
        if course.SKUName4:
            sku_name="%s:%s" %(course.SKUName4,course.SKUValue4)
        if sku_name == '':
            sku_name = None
        Log("UpdateCourseMemberByDate name: %s %s" % (course.Name, sku_name), Type="DEBUG")
        third_party_lesson = LessonsOfThirdParty.objects.filter(Name=course.Name, SKUName=sku_name, ChannelID=2)
        
        #课程默认是有赞
        third_party_lesson = third_party_lesson[0]
                            
        res = UpdateCourseMember(course.ID, third_party_lesson.ID, course.Name, sku_name, third_party_lesson.LessonCategoryID, course_date)
        return HttpResponse(res)
    except Exception,e:
        Log("UpdateCourseMemberByDate error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
#被手动删除过的用户不会被导入
def UpdateCourseMember(course_id, third_party_lesson_id, course_name, sku_name, lesson_category_id, date=''):
    try:
        trades = None
        if sku_name:
            trades = TradeInfo.objects.filter(Name=course_name, SKUName=sku_name, ChannelID=2)
        else:
            trades = TradeInfo.objects.filter(Name=course_name, ChannelID=2)
        if date:
            date = GetDateTimeByStr("%s %s" % (date, "00:00:00"))
            trades = trades.filter(Created__gt=date)
        user_ids = []
        for trade in trades:
            trade.ThirdPartyID = third_party_lesson_id
            trade.LessonCategoryID = lesson_category_id
            trade.save()
            user_ids.append(trade.UserID)
        member_ids = []
        course_member_ids = CloudCourseMember.objects.values("UserID").filter(CloudCourseID=course_id)
        for member_id in course_member_ids:
            if member_id["UserID"] in user_ids:
                user_ids.remove(member_id["UserID"])
        users = User.objects.values("ID","Name","Mobile").filter(ID__in=user_ids)
        for user in users:
            u = CloudCourseMember(CloudCourseID=course_id, Mobile=user['Mobile'], Name=user['Name'], UserID=user['ID'])
            u.save()
        return 'ok'
    except Exception,e:
        Log("UpdateCourseMember error: %s" %e, Type="DEBUG")
        return e
    
    

def DailyClassRemind(request):
    try:
        Log("DailyClassRemaind start", Type="DEBUG")
        today_midnight = (datetime.datetime.today() + timedelta(days = 1)).strftime("%Y-%m-%d 00:00:00")
        tomorrow_midnight = (datetime.datetime.today() + timedelta(days = 2)).strftime("%Y-%m-%d 00:00:00")
        count = 0
        queue = TaskQueue('queue_name')
        url = "/LessonRemindASYNC/"
        tomorrow_lessons = CloudCourseLesson.objects.values("Name", "CloudCourseID", "StartTime").filter(StartTime__gte=today_midnight, StartTime__lt=tomorrow_midnight)
        for lesson in tomorrow_lessons:
            para = {
                "Name": lesson['Name'],
                "CloudCourseID": lesson['CloudCourseID'],
                "StartTime": lesson['StartTime'].strftime("%Y-%m-%d %H:%M"),
                "IsDaily": 1
            }
            queue.add(Task(url,json.dumps(para),delay=2))
            count += 1
            
        
        return HttpResponse(count)
    except Exception,e:
        Log("DailyClassRemaind error: %s" %e, Type="DEBUG")
        return HttpResponse([])
    
    
def HourlyClassRemind(request):
    try:
        #提前1小时提醒
        Log("HourlyClassRemind start", Type="DEBUG")
        time_now = (datetime.datetime.now() + timedelta(minutes = 30)).strftime("%Y-%m-%d %H:%M:%S")
        time_later = (datetime.datetime.now() + timedelta(minutes = 60)).strftime("%Y-%m-%d %H:%M:%S")
        count = 0
        queue = TaskQueue('queue_name')
        url = "LessonRemindASYNC/"
        tomorrow_lessons = CloudCourseLesson.objects.values("Name", "CloudCourseID", "StartTime").filter(StartTime__gte=time_now, StartTime__lte=time_later)
        for lesson in tomorrow_lessons:
            para = {
                "Name": lesson['Name'],
                "CloudCourseID": lesson['CloudCourseID'],
                "StartTime": lesson['StartTime'].strftime("%Y-%m-%d %H:%M"),
                "IsDaily": 0
            }
            queue.add(Task(url,json.dumps(para),delay=2))
            count += 1
        
        return HttpResponse(count)
    except Exception,e:
        Log("HourlyClassRemind error: %s" %e, Type="DEBUG")
        return HttpResponse(e)

@csrf_exempt
def LessonRemindASYNC(request):
    try:
        appid = "wx457b9d0e6f93d1c5"
        wxObj = wxAccountInterface.wxAccountInterface(appid)
        params = json.loads(request.raw_post_data)
        name = params.get("Name")
        cloud_course_id = int(params.get("CloudCourseID"))
        start_time = params.get("StartTime")
        is_daily = int(params.get("IsDaily"))
        course = CloudCourse.objects.get(ID = cloud_course_id)
        course = CloudCourse.objects.get(ID = cloud_course_id)
        students = CloudCourseMember.objects.filter(CloudCourseID = cloud_course_id, IsHide=0)
        for student in students:
            course_name = course.Name.replace("【", "[").replace("】","]")
            if student.Role == 0:
                wxuser = wxUser.objects.values('openID','Name').filter(Mobile=student.Mobile)
                #if is_daily == 1:
                countent = "【外滩教育】 %s，您报名的 %s 课程将于 %s 开始上课，请您在PC上打开上课网址：class.ddianke.com，请合理安排时间，不要错过。感谢您对外滩的支持与信任，如有疑问，请在学习社群内咨询老师。" % (student.Name, course_name, start_time)
                Send106txtTelMsg(student.Mobile,countent,1)
                if not wxuser:
                    continue
                name = student.Name
                if not name:
                    name = wxuser[0]['Name']
                wxObj.SendClassRemindTemplate(name, course.Name, start_time, wxuser[0]['openID'])
            else:
                wxuser = wxUser.objects.values('openID','Name').filter(Mobile=student.Mobile)
                #if is_daily == 1:
                countent = "【外滩教育】 %s，您负责的课程 %s 课程将于 %s 开始上课，请您在PC上打开上课网址：class.ddianke.com，请确认上课时间。如有变动，请及时联系外滩工作人员，感谢您的支持。" % (student.Name, course_name, start_time)
                Send106txtTelMsg(student.Mobile,countent,1)
                if not wxuser:
                    continue
                name = student.Name
                if not name:
                    name = wxuser[0]['Name']
                wxObj.SendTeacherClassRemindTemplate(name, course.Name, start_time, wxuser[0]['openID'])
    except Exception,e:
        Log("LessonRemindASYNC error: %s" %e, Type="DEBUG")
        return HttpResponse([])
    
    
def GetCourseLesson(request):
    try:        
        params = request.GET
        Log("UpdateCourseLesson params: %s" % params, Type="DEBUG")
        course_id = int(params.get('course_id', 0))
        lessons = CloudCourseLesson.objects.values("ID", "Name", "StartTime").filter(CloudCourseID = course_id).order_by("StartTime")
        
        res = []
        for lesson in lessons:
            lesson['StartTime'] = lesson['StartTime'].strftime("%Y-%m-%d %H:%M")
            res.append(lesson)
        #Log("GetAllCoupons obj %s" % obj, Type='DEBUG')
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCourseLesson error: %s" %e, Type="DEBUG")
        return HttpResponse([])
    
    
@csrf_exempt
def UpdateCourseLesson(request):
    try:        
        params = request.POST
        Log("UpdateCourseLesson params: %s" % params, Type="DEBUG")
        course_id = params.get('course_id', 0)
        lessons = params.get('lessons', '')
        if lessons:
            lessons = json.loads(lessons)
        #Log("UpdateCourseLesson lessons: %s" % lessons, Type="DEBUG")
        course = CloudCourse.objects.get(ID = course_id)
        course.Scheduled = 1
        course.save()
        old_lessons = CloudCourseLesson.objects.filter(CloudCourseID = course_id)
        delete_list = []
        for lesson in old_lessons:
            is_delete = True
            for l in lessons:
                if lesson.ID == int(l['lesson_id']):
                    is_delete = False
                    lesson.Name = l['lesson_name']
                    start_time = "%s%s" % (l['start_time'],':00')
                    lesson.StartTime = GetDateTimeByStr(start_time)
                    lesson.save()
            if is_delete:
                delete_list.append(lesson)
        
        for l in lessons:
            if int(l['lesson_id']) == 0:
                start_time = "%s%s" % (l['start_time'],':00')
                #Log("UpdateCourseLesson start_time: %s" % start_time, Type="DEBUG")
                lesson = CloudCourseLesson(CloudCourseID = course_id, Name = l['lesson_name'], StartTime=GetDateTimeByStr(start_time))
                lesson.save()
        
        for d in delete_list:
            d.delete()

        return HttpResponse('ok')
    except Exception,e:
        Log("UpdateCourseLesson error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
def GetUserInfo(request):
    try:
        params = request.GET
        Log("GetUserInfo params: %s" %params, Type="DEBUG")
        mobile = params.get("mobile", 0)
        user = User.objects.filter(Mobile=mobile)
        wxuser = wxUser.objects.filter(SourceAccount = 'wx457b9d0e6f93d1c5',Mobile=mobile)
        res = None
        if wxuser:
            wxuser = wxuser[0]
            if user:
                user = user[0]
                res = {"Name":user.Name, "Avatar":wxuser.Avatar}
            else:
                res = {"Name":wxuser.Name, "Avatar":wxuser.Avatar}
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetUserInfo params: %s" %params, Type="DEBUG")
        return HttpResponse(e)

    
config = {
        'host':'sh-cdb-ps8e2d8e.sql.tencentcdb.com',
        'port':63611,
        'user':'root',
        'password':'TsaiDBPwd!',
        'db':'sbux',
        'charset':'utf8mb4',
        'cursorclass':pymysql.cursors.DictCursor,
    }
    
    
@csrf_exempt
def UploadUsers(request):
    try:
        #Log("UploadCourse", Type="DEBUG")
        params = request.POST
        if request.FILES.has_key("course_file"):
            Log("UploadCourse1", Type="DEBUG")
            teacheres_file = request.FILES["course_file"]
            #csv_reader = csv.reader(classes_file)
            data = xlrd.open_workbook(file_contents=teacheres_file.read())
            table = data.sheets()[1]
            nrows = table.nrows
            line_num = 0
            connection = pymysql.connect(**config)
            try:
                with connection.cursor() as cursor:
                    for i in range(nrows ):
                        row = table.row_values(i)
                        if line_num > 0 and str(row[4].strip()) == '深圳来福士广场店':
                            insert_biz_order = "INSERT INTO Users (CustomerID, CustomerName, Always_Gold_Members, MobileNumber, SelectedStorename, SelectedStoreAddress,SelectedStoreID, Region) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"  % (str(row[0].strip()), str(row[1].strip()), str(row[2].strip()), str(row[3].strip()), str(row[4].strip()), str(row[5].strip()), str(row[6].strip()), str(row[7].strip()))
                            cursor.execute(insert_biz_order)
                        line_num += 1
                    connection.commit()
            except Exception, e:
            #ImportTradeInfo(e, "InsertEdusoho")
                Log("InsertEdusoho error 1:%s"%e, "local", "0.0.0.0", "DEBUG")
            finally:
                connection.close()
        
            return HttpResponse('ok')
        else:
            return HttpResponse('没找到文件')
    except Exception,e:
        Log("UploadCourse error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
        
        
        
        
    