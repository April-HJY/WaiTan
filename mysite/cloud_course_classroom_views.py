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
#import csv
import xlrd
import xlwt
import StringIO
#import pandas as pd
import talk_cloud_interface



def CourseClassroomPage(request):
    template = loader.get_template('courseclassroompage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))

@csrf_exempt
def DivideClass(request):
    try:
        params = request.POST
        Log("DivideClass params: %s" %params, Type="DEBUG")
        course_id = params.get("course_id")
        class_member_count = int(params.get("class_member_count", 1))
        divide_class_type = params.get("divide_class_type", "")
        #course = CloudCourse.objects.get(ID = course_id)
        members = CloudCourseMember.objects.filter(CloudCourseID = course_id, IsHide = 0)
        member_count = len(members)
        class_count = member_count / class_member_count
        class_remainder = member_count % class_member_count
        if class_remainder >0:
            if divide_class_type == 'newclass':
                class_count += 1
        i = 0
        curr_class = None
        class_num = 0
        Log("DivideClass class_count: %d" %class_count, Type="DEBUG")
        Log("DivideClass member_count: %d" %member_count, Type="DEBUG")
        while i < member_count:
            Log("DivideClass 1", Type="DEBUG")
            if i % class_member_count == 0:
                Log("DivideClass 2", Type="DEBUG")
                class_num += 1
                if class_num <= class_count:
                    Log("DivideClass 3", Type="DEBUG")
                    name = "class%d" % class_num
                    curr_class = CloudClass(CloudCourseID = course_id, Name=name)
                    curr_class.save()
            member = members[i]
            member.CloudClassID = curr_class.ID
            member.Updated = datetime.datetime.now()
            member.save()
            i += 1
        return HttpResponse('ok')
    except Exception,e:
        Log("DivideClass error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
def ClassStart(request):
    try:
        params = request.GET
        Log("ClassStart params: %s" %params, Type="DEBUG")
        serial = params.get("serial",0)
        classroom = CloudClassRoom.objects.filter(Serial=serial)
        if classroom:
            classroom[0].ClassStart = 1
            classroom[0].Updated = datetime.datetime.now()
            classroom[0].save()
        return HttpResponse('ok')
    except Exception,e:
        Log("ClassStart error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
def ClassEnd(request):
    try:
        params = request.GET
        Log("ClassEnd params: %s" %params, Type="DEBUG")
        serial = params.get("serial",0)
        classroom = CloudClassRoom.objects.filter(Serial=serial)
        if classroom:
            classroom[0].ClassStart = 2
            classroom[0].Updated = datetime.datetime.now()
            classroom[0].save()
        return HttpResponse('ok')
    except Exception,e:
        Log("ClassEnd error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
def GetClassrooms(request):
    try:
        params = request.GET
        Log("GetClassrooms params: %s" %params, Type="DEBUG")
        is_valid = params.get("is_valid",0)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        Log("GetClassrooms today: %s" %today, Type="DEBUG")
        start_time = params.get("start_time",today)
        end_time = params.get("end_time",today)
        #start_time = time.strptime("%s 00:00:00" % start_time, "%Y-%m-%d %H:%M:%S")
        #end_time = time.strptime("%s 23:59:59" % end_time, "%Y-%m-%d %H:%M:%S")
        start_time = "%s 00:00:00" % start_time
        end_time = "%s 23:59:59" % end_time
        Log("GetClassrooms start_time: %s" %start_time, Type="DEBUG")
        Log("GetClassrooms end_time: %s" %end_time, Type="DEBUG")
        classrooms = CloudClassRoom.objects.values("ID","Name","CloudCourseID","CloudClassID","CloudCourseLessonID","Serial","StartTime","TeacherPwd","PatrolPwd","AssistantPwd","StudentPwd","ClassStart")\
            .filter(Q(StartTime__gte=start_time, StartTime__lte=end_time) | Q(EndTime__gte=start_time, EndTime__lte=end_time))
        Log("GetClassrooms classrooms: %s" %classrooms, Type="DEBUG")
        course_ids = []
        class_ids = []
        lesson_ids = []
        for classroom in classrooms:
            if classroom['CloudCourseID'] not in course_ids:
                course_ids.append(classroom['CloudCourseID'])
            if classroom['CloudClassID'] not in class_ids:
                class_ids.append(classroom['CloudClassID'])
            if classroom['CloudCourseLessonID'] not in lesson_ids:
                lesson_ids.append(classroom['CloudCourseLessonID'])
        courses = CloudCourse.objects.values("ID","Name").filter(ID__in=course_ids)
        classes = CloudClass.objects.values("ID","Name").filter(ID__in=class_ids)
        lessons = CloudCourseLesson.objects.values("ID","Name","StartTime").filter(ID__in=lesson_ids)
        res = []
        for classroom in classrooms:
            for course in courses:
                if classroom['CloudCourseID'] == course["ID"]:
                    classroom['CourseName'] = course["Name"]
            for _class in classes:
                if classroom['CloudClassID'] == _class["ID"]:
                    classroom['ClassName'] = _class["Name"]
            for lesson in lessons:
                if classroom['CloudCourseLessonID'] == lesson["ID"]:
                    classroom['LessonStartTime'] = lesson["StartTime"].strftime("%Y-%m-%d %H:%M")
            classroom['StartTime'] = classroom['StartTime'].strftime("%Y-%m-%d %H:%M")
            if classroom['ClassStart'] == 1:
                url = talk_cloud_interface.GetClassroomURL(classroom['Serial'],'巡课',4,time.time(),classroom['PatrolPwd'])
                classroom['ClassStart'] = '<a href="%s" target="_blank">上课中</a>' % url
            elif classroom['ClassStart'] == 2:
                classroom['ClassStart'] = '已结束'
            else:
                classroom['ClassStart'] = '未开始'
            classroom['Edit'] = "<a href='javascript:delete_classroom(%d)'>删除</a> <a href='javascript:showUploadWare(%d)'>关联课件</a>" % (classroom['Serial'],classroom['Serial'])
            res.append(classroom)
            
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetClassrooms error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
def HourlyStartClassRoom(request):
    try:
        #上课前24小时创建教室
        before_kick_off = 24
        duration_hours = 27
        Log("HourlyStartClassRoom start", Type="DEBUG")
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_later = (datetime.datetime.now() + timedelta(hours = 25)).strftime("%Y-%m-%d %H:%M:%S")
        count = 0
        queue = TaskQueue('queue_name')
        url = "/HourlyLessonRemindASYNC/"
        lessons = CloudCourseLesson.objects.values("ID", "Name", "CloudCourseID", "StartTime").filter(StartTime__gte=time_now, StartTime__lte=time_later)
        Log("HourlyStartClassRoom lessons %s" % lessons, Type="DEBUG")
        for lesson in lessons:
            curr_classes = CloudClass.objects.values("ID", "Name").filter(CloudCourseID = lesson['CloudCourseID'])
            Log("HourlyStartClassRoom curr_classes %s" % curr_classes, Type="DEBUG")
            for curr_class in curr_classes:
                course_id = lesson['CloudCourseID']
                class_id = curr_class['ID']
                lesson_id = lesson['ID']
                name = curr_class["Name"]
                chairmanpwd = random_verificaioncode(4)
                assistantpwd = random_verificaioncode(4)
                patrolpwd = random_verificaioncode(4)
                confuserpwd = random_verificaioncode(4)
                start_time = lesson['StartTime'] + timedelta(hours = -before_kick_off)
                end_time = start_time + timedelta(hours = duration_hours)
                class_room = CloudClassRoom.objects.filter(CloudCourseID=course_id, CloudClassID=class_id, CloudCourseLessonID=lesson_id)
                if class_room:
                    continue;
                res = talk_cloud_interface.CreateClass(name, chairmanpwd, assistantpwd, patrolpwd, confuserpwd, start_time, end_time)
                if not res:
                    continue;
                class_room = CloudClassRoom(CloudCourseID=course_id, CloudClassID=class_id, CloudCourseLessonID=lesson_id, Name=name, Serial=res['serial'], Version=res['version'], 
                                            StartTime=start_time, EndTime=end_time, TeacherPwd=chairmanpwd, PatrolPwd=patrolpwd, AssistantPwd=assistantpwd, StudentPwd=confuserpwd)
                class_room.save()
                count += 1
        
        return HttpResponse(count)
    except Exception,e:
        Log("HourlyStartClassRoom error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
def DeleteClassroom(request):
    try:
        params = request.POST
        serial = int(params.get('serial',0))
        res = talk_cloud_interface.DeleteClassroom(serial)
        Log("DeleteClassroom result: %d"%res['result'], Type="DEBUG")
        if res['result'] == 0:
            classroom = CloudClassRoom.objects.get(Serial=serial)
            classroom.delete()
        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteClassroom error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
    