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
import decimal

def LessonPage(request):
    template = loader.get_template('lessonpage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))


def ThirdPartyLessonPage(request):
    template = loader.get_template('lessonsofthirdpartypage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))


def MappingPage(request):
    template = loader.get_template('mappingpage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))


def GetCatetories(request):
    try:
        categories = getVar("LessonCategory")
        res = []
        for cate in categories:
            res.append({"ID":cate.ID, "Name":cate.Name})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetCatetories error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

    
def GetCateDic():
    cate_dic = {}
    categories = getVar("LessonCategory")
    for cate in categories:
        cate_dic[cate.ID] = cate.Name
    return cate_dic

def GetLessons(request):
    try:
        params = request.GET
        res = []
        condition = params.get('condition')
        channel_id = params.get('channel_id',None)
        cate_dic = GetCateDic()
        
        lessons = getVar("Lesson")
        if channel_id and channel_id != 'all':
            lessons = lessons.filter(ChannelID=int(channel_id))
        if condition:
            lessons = lessons.filter(Q(Name__contains=str(condition).strip()) | Q(Code=str(condition).strip()))
        third_party_lessons = LessonsOfThirdParty.objects.filter(ChannelID=1)
        for lesson in lessons:
            cate_id = 5
            for third_party_l in third_party_lessons:
                if third_party_l.Name == lesson.Name and third_party_l.SKUName == lesson.TeachingPlan:
                    cate_id = third_party_l.LessonCategoryID
                    break;
            edit = "<a href='javascript:edit_lesson(%d)'>修改</a>&nbsp;<a href='javascript:delete_lesson(%d)'>删除</a>" % (lesson.ID,lesson.ID)
            res.append({"ID":lesson.ID,"Name":lesson.Name, "Code":lesson.Code,"TeachingPlan":lesson.TeachingPlan,"Edit":edit, "Category": cate_dic[cate_id]})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetLessons error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def SaveLesson(request):
    try:
        params = request.POST
        Log("SaveLesson params: %s" % params, "local", "0.0.0.0", "DEBUG")
        update_id = params.get('id', None)
        code = params.get('code')
        cname = params.get('cname')
        teachingplan = params.get('teachingplan', None)
        cate_id = params.get('cate_id', 5)
        thirdpartyname = ''
        skuname = None
        if not teachingplan or teachingplan == '-':
            teachingplan = None
        if update_id:
            lesson = Lesson.objects.get(ID=update_id)
            thirdpartyname = lesson.Name
            skuname = lesson.TeachingPlan
            lesson.Code = code
            lesson.Name = cname
            lesson.TeachingPlan = teachingplan
            lesson.save()
        else:
            lesson = Lesson(Code=code, Name=cname, TeachingPlan=teachingplan)
            lesson.save()
        #需要同步修改ThirdPartyLesson里大指课程
        thirdpartylesson = LessonsOfThirdParty.objects.filter(Name=thirdpartyname, SKUName=skuname, ChannelID=1)
        if thirdpartylesson:
            thirdpartylesson[0].Name = cname
            thirdpartylesson[0].SKUName = teachingplan
            thirdpartylesson[0].TelMsgTemplateID=0
            thirdpartylesson[0].LessonCategoryID=cate_id
            thirdpartylesson[0].save()
        else:
            thirdpartylesson = LessonsOfThirdParty(Name=cname, SKUName=teachingplan, ChannelID=1, TelMsgTemplateID=0,LessonCategoryID=cate_id)
            thirdpartylesson.save()
        updateVar("Lesson")
        updateVar("LessonsOfThirdParty")
        return HttpResponse('ok')
    except Exception,e:
        Log("SaveLesson error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def DeleteLesson(request):
    try:
        params = request.POST
        Log("DeleteLesson params: %s" % params, "local", "0.0.0.0", "DEBUG")
        delete_id = params.get('id', None)
        
        if delete_id:
            lesson = Lesson.objects.get(ID=delete_id)
            lesson.delete()
        updateVar("Lesson")
        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteLesson error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
    
def GetThirdPartyLessons(request):
    try:
        params = request.GET
        res = []
        condition = params.get('condition')
        channel_id = params.get('channel_id',None)
        cate_dic = GetCateDic()
        channel_dic = GetChannelRemarkDic();
        lessons = getVar("LessonsOfThirdParty")
        if channel_id and channel_id != 'all':
            lessons = lessons.filter(ChannelID=int(channel_id))
        if condition:
            lessons = lessons.filter(Name__contains=str(condition).strip())

        for lesson in lessons:
            edit = ''
            if lesson.ChannelID == 2 or lesson.ChannelID == 15:
                edit = "<a href='javascript:lesson_mapping(%d)'>对照表</a>&nbsp;" % lesson.ID
            edit += "<a href='javascript:edit_lesson(%d)'>修改</a>&nbsp;<a href='javascript:delete_lesson(%d)'>删除</a>" % (lesson.ID,lesson.ID)
            res.append({"ID":lesson.ID,"Channel":channel_dic[lesson.ChannelID],"Name":lesson.Name, "SKUName":lesson.SKUName,"MsgID":lesson.TelMsgTemplateID,"Edit":edit, "Category": cate_dic[lesson.LessonCategoryID]})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetThirdPartyLessons error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def SaveThirdPartyLesson(request):
    try:
        params = request.POST
        Log("SaveThirdPartyLesson params: %s" % params, "local", "0.0.0.0", "DEBUG")
        update_id = params.get('id', None)
        cname = params.get('cname')
        skuname = params.get('skuname', None)
        cate_id = params.get('cate_id', 5)
        channel_id = params.get('channel_id', 5)
        msg_id = params.get('msg_id', 0)
        thirdpartyname = ''
        if not skuname or skuname == '-':
            skuname = None
        if update_id:
            lesson = LessonsOfThirdParty.objects.get(ID=update_id)
            lesson.Name = cname
            lesson.SKUName = skuname
            Log("SaveThirdPartyLesson lesson.SKUName: %s" % lesson.SKUName, "local", "0.0.0.0", "DEBUG")
            lesson.LessonCategoryID = cate_id
            lesson.ChannelID = channel_id
            lesson.TelMsgTemplateID = msg_id
            lesson.save()
        else:
            lesson = LessonsOfThirdParty(ChannelID=channel_id,Name=cname, SKUName=skuname, LessonCategoryID=cate_id, TelMsgTemplateID=msg_id)
            lesson.save()

        updateVar("LessonsOfThirdParty")
        return HttpResponse('ok')
    except Exception,e:
        Log("SaveThirdPartyLesson error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def DeleteThirdPartyLesson(request):
    try:
        params = request.POST
        Log("DeleteThirdPartyLesson params: %s" % params, "local", "0.0.0.0", "DEBUG")
        delete_id = params.get('id', None)
        
        if delete_id:
            lesson = LessonsOfThirdParty.objects.get(ID=delete_id)
            lesson.delete()
        updateVar("LessonsOfThirdParty")
        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteThirdPartyLesson error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetLessonMapping(request):
    try:
        params = request.GET
        Log("GetLessonMapping params:%s"%params, "local", "0.0.0.0", "DEBUG")
        res = []
        thirdparty_id = params.get('thirdparty_id',None)
        cate_dic = GetCateDic()
        channel_dic = GetChannelRemarkDic();
        thirdpartylesson = LessonsOfThirdParty.objects.get(ID=thirdparty_id)
        lesson_ids = []
        lesson_relations = LessonsRelation.objects.values('ID','LessonID').filter(ThirdPartyID=thirdparty_id)
        for relation in lesson_relations:
            lesson_ids.append(relation['LessonID'])
        lessons = Lesson.objects.filter(ID__in=lesson_ids)
        for lesson in lessons:
            relation_id = 0
            for relation in lesson_relations:
                if relation['LessonID'] == lesson.ID:
                    relation_id = relation['ID']
                    break;
            edit = "<a href='javascript:delete_relation(%d)'>取消关联</a>" % (relation_id)
            res.append({"ID":lesson.ID,"Name":lesson.Name, "Code":lesson.Code,"TeachingPlan":lesson.TeachingPlan,"Edit":edit, "Category": cate_dic[thirdpartylesson.LessonCategoryID]})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetLessonMapping error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetLessonMappingNew(request):
    try:
        params = request.GET
        Log("GetLessonMappingNew params:%s"%params, "local", "0.0.0.0", "DEBUG")
        res = []
        thirdparty_id = params.get('thirdparty_id',None)
        condition_new = params.get('condition_new',None)
        cate_dic = GetCateDic()
        channel_dic = GetChannelRemarkDic();
        thirdpartylesson = LessonsOfThirdParty.objects.get(ID=thirdparty_id)
        lesson_ids = []
        lesson_relations = LessonsRelation.objects.values('ID','LessonID').filter(ThirdPartyID=thirdparty_id)
        for relation in lesson_relations:
            lesson_ids.append(relation['LessonID'])
        lessons = None
        if condition_new:
            lessons = Lesson.objects.filter(Q(Name__contains=str(condition_new).strip()) | Q(Code=str(condition_new).strip()))
        else:
            lessons = Lesson.objects.all()
        third_party_lessons = LessonsOfThirdParty.objects.filter(ChannelID=1)
        for lesson in lessons:
            cate_id = 5
            if lesson.ID in lesson_ids:
                continue
            for third_party_l in third_party_lessons:
                if third_party_l.Name == lesson.Name and third_party_l.SKUName == lesson.TeachingPlan:
                    cate_id = third_party_l.LessonCategoryID
                    break;
            edit = "<a href='javascript:relate_lesson(%d)'>关联</a>" % (lesson.ID)
            res.append({"ID":lesson.ID,"Name":lesson.Name, "Code":lesson.Code,"TeachingPlan":lesson.TeachingPlan,"Edit":edit, "Category": cate_dic[cate_id]})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetLessonMappingNew error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def RelateLesson(request):
    try:
        params = request.POST
        Log("RelateLesson params: %s" % params, "local", "0.0.0.0", "DEBUG")
        lesson_id = params.get('id', None)
        thirdparty_id = params.get('thirdparty_id', None)
        
        if lesson_id and thirdparty_id:
            lesson = LessonsRelation.objects.filter(LessonID=lesson_id, ThirdPartyID=thirdparty_id)
            if not lesson:
                lesson = LessonsRelation(LessonID=lesson_id, ThirdPartyID=thirdparty_id)
                lesson.save()
        updateVar("LessonsRelation")
        return HttpResponse('ok')
    except Exception,e:
        Log("RelateLesson error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def DeleteRelation(request):
    try:
        params = request.POST
        Log("DeleteRelation params: %s" % params, "local", "0.0.0.0", "DEBUG")
        delete_id = params.get('id', None)
        
        if delete_id:
            lesson = LessonsRelation.objects.get(ID=delete_id)
            lesson.delete()
        updateVar("LessonsRelation")
        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteRelation error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
    
