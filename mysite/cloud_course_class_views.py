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



def CourseClassPage(request):
    template = loader.get_template('courseclasspage.html')
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
    
    
@csrf_exempt
def UploadTeacher(request):
    try:
        params = request.POST
        if request.FILES.has_key("teacher_file"):
            teacheres_file = request.FILES["teacher_file"]
            #csv_reader = csv.reader(classes_file)
            data = xlrd.open_workbook(file_contents=teacheres_file.read())
            table = data.sheets()[0]
            nrows = table.nrows
            line_num = 0
            for i in range(nrows ):
                row = table.row_values(i)
            #for row in csv_reader:
                if line_num == 0:
                    if str(row[0].strip()) != u"老师姓名" or row[1].strip() != u"电话":
                        return HttpResponse('列名不对，请确认是否传错文件')
                if line_num > 0:
                    teacher_name = row[0].strip()
                    #姓名为空不导入
                    if not teacher_name:
                        continue
                    #电话无效不导入
                    mobile = 0
                    try:
                        mobile = int(row[1])
                    except Exception,e:
                        mobile = 0
                    if mobile == 0:
                        continue;
                    
                    #老师都是大指渠道，已有用户不改渠道
                    teacher = User.objects.filter(Mobile=mobile)
                    if teacher:
                        teacher[0].Name = teacher_name
                        teacher[0].Role = 1
                        teacher[0].save()
                    else:
                        teacher = User(Mobile=mobile, Name=teacher_name, ChannelID=1, Role=1, DistributorName=None, NickName=None)
                        teacher.save()

                    #Log("UploadClasses row %s" % row, Type="DEBUG")
                line_num += 1
        
        #CloudClass.objects.filter(CloudCourseID = course_id).delete()
        #CloudCourseMember.objects.filter(CloudCourseID=course_id).update(CloudClassID = None)
        
            return HttpResponse('ok')
        else:
            return HttpResponse('没找到文件')
    except Exception,e:
        Log("UploadTeacher error: %s" %e, Type="DEBUG")
        return HttpResponse(e)    
    
@csrf_exempt
def UploadClasses(request):
    try:
        params = request.POST
        course_id = params.get("course_id")
        classes = CloudClass.objects.filter(CloudCourseID = course_id);
        if classes:
            return HttpResponse('已有分班')
        if request.FILES.has_key("classes_file"):
            classes_file = request.FILES["classes_file"]
            #csv_reader = csv.reader(classes_file)
            data = xlrd.open_workbook(file_contents=classes_file.read())
            table = data.sheets()[0]
            nrows = table.nrows
            line_num = 0
            for i in range(nrows ):
                row = table.row_values(i)
            #for row in csv_reader:
                if line_num == 0:
                    if str(row[0].strip()) != u"班级名称" or row[1].strip() != u"学员电话":
                        return HttpResponse('列名不对，请确认是否传错文件')
                if line_num > 0:
                    class_name = row[0].strip()
                    #班级为空不导入
                    if not class_name:
                        continue
                    #电话无效不导入
                    mobile = 0
                    try:
                        mobile = int(row[1])
                    except Exception,e:
                        mobile = 0
                    if mobile == 0:
                        continue;
                    student = CloudCourseMember.objects.filter(CloudCourseID=course_id, Mobile=mobile, IsHide = 0)
                    #自动添加学员
                    if not student:
                        user = User.objects.filter(Mobile=mobile)
                        if not user:
                            continue;
                        name = user[0].ChildName
                        if not name:
                            name = user[0].Name
                        student = CloudCourseMember(CloudCourseID=course_id, Mobile=mobile, IsHide = 0, Name=name, UserID=user[0].ID)
                    else:
                        student = student[0]
                    c = CloudClass.objects.filter(CloudCourseID = course_id, Name=str(class_name))
                    if not c:
                        c = CloudClass(CloudCourseID = course_id, Name=class_name)
                        c.save()
                    else:
                        c = c[0]
                    student.CloudClassID = c.ID
                    student.save()
                    #Log("UploadClasses row %s" % row, Type="DEBUG")
                line_num += 1
        
        #CloudClass.objects.filter(CloudCourseID = course_id).delete()
        #CloudCourseMember.objects.filter(CloudCourseID=course_id).update(CloudClassID = None)
        
            return HttpResponse('ok')
        else:
            return HttpResponse('没找到文件')
    except Exception,e:
        Log("UploadClasses error: %s" %e, Type="DEBUG")
        return HttpResponse(e)


def GetCloudCoursesForClass(request):
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
            lessons = CloudCourseLesson.objects.values("StartTime").filter(CloudCourseID=course.ID).order_by("StartTime")
            if not lessons:
                continue
            member_count = CloudCourseMember.objects.filter(CloudCourseID=course.ID, IsHide = 0,Role=0).count()
            member_count_not_in_class = CloudCourseMember.objects.filter(CloudCourseID=course.ID, IsHide = 0,Role=0,CloudClassID=None).count()
            
            classes = CloudClass.objects.values("ID").filter(CloudCourseID=course.ID)
            if not classes:
                is_divide = 0
                edit = "<a href='javascript:popShow(%d)'>建立分班</a>" % (course.ID)
            else:
                is_divide = len(classes)
                edit = "<a href='javascript:popShow(%d)'>查看或修改</a>" % (course.ID)
            sku = "%s %s %s %s" % (course.SKUValue1 if course.SKUValue1 else '', course.SKUValue2 if course.SKUValue2 else '', course.SKUValue3 if course.SKUValue3 else '', course.SKUValue4 if course.SKUValue4 else '')
            res.append({"ID":course.ID, "Name":course.Name, "FirstLessonTime":lessons[0]['StartTime'].strftime("%Y-%m-%d %H:%M"), "MemberCount": member_count, "MemberCountNotInClass":member_count_not_in_class, 
                        "SKU": sku, "Edit": edit, "IsDivided":is_divide})
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
        Log("GetCloudCoursesForClass error: %s" %e, Type="DEBUG")
        return HttpResponse('')

    
def GetCloudCourseClasses(request):
    try:
        params = request.GET
        course_id = params.get("course_id")
        classes = CloudClass.objects.values("ID","Name", "PatrolInfo").filter(CloudCourseID = course_id).order_by("ID")
        members = CloudCourseMember.objects.values("CloudClassID", "Role", "Name").filter(CloudCourseID=course_id)
        res = []
        for c in classes:
            member_count = 0
            for member in members:
                if member['CloudClassID'] == c["ID"]:
                    if member['Role'] == 1:
                        Log("GetCloudCourseClasses teacher", Type="DEBUG")
                        c['TeacherName'] = member['Name']
                        
                    else:
                        #c['TeacherName'] = ''
                        member_count += 1
                
            #member_count = CloudCourseMember.objects.values("ID").filter(CloudClassID=c['ID']).count()
            edit = "<a href='javascript:show_class(%d)'>修改</a>" % (c['ID'])
            c['Edit'] = edit
            c['count'] = member_count
            res.append(c)   
            Log("GetCloudCourseClasses res: %s " % res, Type="DEBUG")
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCloudCourseClasses error: %s" %e, Type="DEBUG")
        return HttpResponse('')
    
    
def GetCloudCourseClassMember(request):
    try:
        params = request.GET
        course_id = params.get("course_id")
        class_id = params.get("class_id")
        members = CloudCourseMember.objects.values("ID","Name","Mobile").filter(CloudCourseID = course_id, CloudClassID= class_id, IsHide = 0, Role=0).order_by("ID")
        res = []
        for c in members:
            edit = "<a href='javascript:showEditMember(%d)'>修改</a>   <a href='javascript:deleteMember(%d)'>删除</a>" % (c['ID'],c['ID'])
            c['Edit'] = edit
            res.append(c)   
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCloudCourseClassMember error: %s" %e, Type="DEBUG")
        return HttpResponse('')
    
@csrf_exempt
def UpdateMember(request):
    try:
        params = request.POST
        member_id = params.get("member_id")
        member_name = params.get("member_name")
        member = CloudCourseMember.objects.get(ID = member_id)
        member.Name = member_name
        member.save()
        #是否修改User表中的Name 
        return HttpResponse('ok')
    except Exception,e:
        Log("GetCloudCourseClassMember error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
def GetTeachers(request):
    try:
        params = request.GET
        course_id = params.get("course_id")
        mobile = params.get("mobile")
        members = CloudCourseMember.objects.values("UserID").filter(CloudCourseID = course_id, IsHide = 0, Role=0)
        member_ids = []
        for member in members:
            member_ids.append(member['UserID'])
        teachers = None
        if mobile:
            teachers = User.objects.values("ID","Name","Mobile").filter(~Q(ID__in=member_ids),Mobile=mobile, Role=1).order_by("ID")
        else:
            teachers = User.objects.values("ID","Name","Mobile").filter(~Q(ID__in=member_ids),Role=1).order_by("ID")
            
        res = []
        count = 0
        for c in teachers:
            edit = ''
            edit = "<a href='javascript:choose_teacher(%d)'>选择</a>" % (c['ID'])
            c['Edit'] = edit
            res.append(c)
            count += 1
            if count >= 100:
                break;
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetTeachers error: %s" %e, Type="DEBUG")
        return HttpResponse(json.dumps([]))
    
    
    
#没有买课程的学员添加也用这个
def GetCloudCourseMemberNotInClass(request):
    try:
        params = request.GET
        course_id = params.get("course_id")
        mobile = params.get("mobile")
        is_all_user = int(params.get("is_all_user", 0))
        Log("GetCloudCourseMemberNotInClass params: %s" %params, Type="DEBUG")
        members = None
        if mobile:
            members = CloudCourseMember.objects.values("ID","UserID","Name","Mobile").filter(CloudCourseID = course_id, CloudClassID= None, IsHide = 0, Mobile=mobile, Role=0).order_by("ID")
        else:
            members = CloudCourseMember.objects.values("ID","UserID","Name","Mobile").filter(CloudCourseID = course_id, CloudClassID= None, IsHide = 0, Role=0).order_by("ID")
        
        if is_all_user:
            user_ids = []
            for c in members:
                user_ids.append(c['UserID'])
            if mobile:
                members = User.objects.values("ID","Name","Mobile").filter(Mobile=mobile, Role=0).filter(~Q(ID__in=user_ids)).order_by("ID")
            else:
                members = User.objects.values("ID","Name","Mobile").filter(~Q(ID__in=user_ids), Role=0).order_by("ID")
        
        res = []
        count = 0
        for c in members:
            edit = ''
            if is_all_user:
                edit = "<a href='javascript:add_to_course(%d)'>添加</a>" % (c['ID'])
            else:
                edit = "<a href='javascript:add_to_class(%d)'>添加</a>" % (c['ID'])
            c['Edit'] = edit
            res.append(c)
            count += 1
            if count >= 100:
                break;
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCloudCourseMemberNotInClass error: %s" %e, Type="DEBUG")
        return HttpResponse('')
    
    
    
def ExportCourseClass(request):
    try:
        params = request.GET
        course_id = params.get("course_id")
        course = CloudCourse.objects.values("Name").get(ID=course_id)
        course_classes = CloudClass.objects.values("ID","Name").filter(CloudCourseID=course_id).order_by("ID")
        course_members = CloudCourseMember.objects.values("ID","CloudClassID","Mobile","Name").filter(CloudCourseID=course_id, Role=0)
        if not course_classes or not course_members:
            return HttpResponse("没有分班信息")
        ws = xlwt.Workbook(encoding='utf-8')
        w = ws.add_sheet(u"分班信息")
        w.write(0, 0, u"班级名称")
        w.write(0, 1, u"学员电话")
        w.write(0, 2, u"学员姓名（此列不是导入信息）")
        line_num = 1
        for course_class in course_classes:
            for course_member in course_members:
                if course_class['ID'] == course_member["CloudClassID"]:
                    w.write(line_num, 0, course_class['Name'])
                    w.write(line_num, 1, course_member['Mobile'])
                    w.write(line_num, 2, course_member['Name'])
                    line_num += 1

        sio = StringIO.StringIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(),
        content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=%s.xls' % time.strftime('%Y%m%d%H%M%S')
        response.write(sio.getvalue())
        return response        
    except Exception,e:
        Log("ExportCourseClass error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
#课程的所有学员
def GetCloudCourseMember(request):
    try:
        params = request.GET
        course_id = params.get("course_id")
        mobile = params.get("mobile")
        members = None
        if mobile:
            members = CloudCourseMember.objects.values("ID","UserID","Name","Mobile","CloudClassID", "Role").filter(CloudCourseID = course_id, IsHide = 0, Mobile=mobile).order_by("ID")
        else:
            members = CloudCourseMember.objects.values("ID","UserID","Name","Mobile","CloudClassID", "Role").filter(CloudCourseID = course_id, IsHide = 0).order_by("ID")
        
        course_classes = CloudClass.objects.values("ID","Name").filter(CloudCourseID=course_id)
        res = []
        count = 0
        for c in members:
            class_name = ''
            if c['Role'] == 1:
                continue;
            for course_class in course_classes:
                if course_class['ID'] == c['CloudClassID']:
                    class_name = course_class['Name']
            c['ClassName'] = class_name
            edit = "<a href='javascript:remove_from_course(%d)'>删除</a>" % (c['ID'])
            c['Edit'] = edit
            res.append(c)
            count += 1
            if count >= 100:
                break;
        return HttpResponse(json.dumps(res))
    except Exception,e:
        Log("GetCloudCourseMember error: %s" %e, Type="DEBUG")
        return HttpResponse('')
    

@csrf_exempt    
def UpdateClassInfo(request):
    try:
        params = request.POST
        course_id = params.get("course_id")
        class_id = params.get("class_id")
        #目前只有名称，将来会有老师班主任等信息
        class_name = params.get("class_name")
        teacher_id = params.get("teacher_id", None)
        patrol_info = params.get("patrol_info", None)
        new_class = CloudClass.objects.filter(ID = class_id)

        if not new_class:
            return HttpResponse('没找到班级')
        new_class[0].Name = class_name
        new_class[0].PatrolInfo = patrol_info
        new_class[0].Updated = datetime.datetime.now()
        new_class[0].save()
        if teacher_id:
            teacher = User.objects.filter(ID = teacher_id, Role = 1)        
            class_teacher = CloudCourseMember.objects.filter(CloudClassID = class_id, Role = 1)
            if class_teacher:
                class_teacher[0].Name = teacher[0].Name
                class_teacher[0].Mobile = teacher[0].Mobile
                class_teacher[0].UserID = teacher[0].ID
                class_teacher[0].Updated = datetime.datetime.now()
                class_teacher[0].save()
            else:
                class_teacher = CloudCourseMember(CloudClassID = class_id, Role = 1, Name= teacher[0].Name, UserID = teacher[0].ID, Mobile = teacher[0].Mobile, CloudCourseID = course_id)
                class_teacher.save()
        return HttpResponse('ok')
    except Exception,e:
        Log("UpdateClassInfo error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt  
def AddStudentToClass(request):
    try:
        params = request.POST
        class_id = params.get("class_id")
        #为CloudCourseMember表id
        student_id = params.get("student_id")
        new_class = CloudClass.objects.filter(ID = class_id)
        if not new_class:
            return HttpResponse('没找到班级')
        student = CloudCourseMember.objects.filter(ID = student_id, CloudCourseID = new_class[0].CloudCourseID)
        if not student:
            return HttpResponse('没找到学员，或学员没报名此课程')
        student[0].CloudClassID = new_class[0].ID
        student[0].Updated = datetime.datetime.now()
        student[0].save()
        
        return HttpResponse('ok')
    except Exception,e:
        Log("AddStudentToClass error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt    
def RemoveStudentFromClass(request):
    try:
        params = request.POST
        Log("RemoveStudentFromClass params: %s" %params, Type="DEBUG")
        class_id = params.get("class_id")
        #为CloudCourseMember表id
        student_id = params.get("student_id")
        new_class = CloudClass.objects.filter(ID = class_id)
        if not new_class:
            return HttpResponse('没找到班级')
        student = CloudCourseMember.objects.filter(ID = student_id, CloudClassID=new_class[0].ID)
        if not student:
            return HttpResponse('没找到学员，或学员不在此班级')
        student[0].CloudClassID = None
        student[0].save()
        
        return HttpResponse('ok')
    except Exception,e:
        Log("RemoveStudentFromClass error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt    
def AddStudentToCourse(request):
    try:
        params = request.POST
        course_id = params.get("course_id")
        #为user表id
        user_id = params.get("user_id")
        course = CloudCourse.objects.filter(ID = course_id)
        if not course:
            return HttpResponse('没找到课程')
        user = User.objects.filter(ID = user_id)
        if not user:
            return HttpResponse('没找到学员')
        student = CloudCourseMember.objects.filter(UserID = user[0].ID, CloudCourseID = course_id)
        if student:
            student[0].IsHide = 0
            student[0].save()
        else:
            name = user[0].ChildName
            if not name:
                name = user[0].Name
            student = CloudCourseMember(Mobile = user[0].Mobile, CloudCourseID = course_id, Name=name, UserID = user[0].ID)
            student.save()
        
        return HttpResponse('ok')
    except Exception,e:
        Log("AddStudentToCourse error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt    
def RemoveStudentFromCourse(request):
    try:
        params = request.POST
        course_id = params.get("course_id")
        #为CloudCourseMember表id
        student_id = params.get("student_id")
        course = CloudCourse.objects.filter(ID = course_id)
        if not course:
            return HttpResponse('没找到课程')

        student = CloudCourseMember.objects.filter(ID = student_id, CloudCourseID = course_id)
        if student:
            student[0].IsHide = 1
            student[0].CloudClassID = None
            student[0].save()
        
        return HttpResponse('ok')
    except Exception,e:
        Log("RemoveStudentFromCourse error: %s" %e, Type="DEBUG")
        return HttpResponse(e)

    
@csrf_exempt
def ClearClasses(request):
    try:
        params = request.POST
        course_id = params.get("course_id")
        CloudClass.objects.filter(CloudCourseID = course_id).delete()
        CloudCourseMember.objects.filter(CloudCourseID=course_id, Role=0).update(CloudClassID = None)
        CloudCourseMember.objects.filter(CloudCourseID=course_id, Role=1).delete()
        
        return HttpResponse('ok')
    except Exception,e:
        Log("ClearClasses error: %s" %e, Type="DEBUG")
        return HttpResponse(e)

    


