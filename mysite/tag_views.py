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
import student_views

        
def TagPage(request):
    template = loader.get_template('tagview.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 


def GetTags(request):
    tags = getVar('UserTag')
    res = []
    for tag in tags:
        res.append({"ID":tag.ID, "Name":tag.Name, "Description": tag.Description, "TagType": tag.TagType, "Created": tag.Created.strftime("%Y-%m-%d %H:%M:%S"), "NickName": tag.NickName})
    return HttpResponse(json.dumps(res))


@csrf_exempt
def AddTag(request):
    params = request.POST
    try:
        name = params.get('name')
        desc = params.get('desc')
        rules = params.get('rules')
        u = UserTag(Name=name, Description = desc, Rules= rules)
        u.save()
        updateVar('UserTag')
        return HttpResponse('ok')
    except Exception,e:
        Log("AddTag error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

@csrf_exempt
def UpdateTag(request):
    params = request.POST
    try:
        tag_id = 0
        if params.get('id'):
            tag_id = int(params.get('id'))
        name = params.get('name')
        desc = params.get('desc')
        rules = params.get('rules')
        unionid = params.get('unionid')
        wx_user = wxUser.objects.filter(unionID=unionid)
        nickname = ''
        if wx_user:
            nickname = wx_user[0].Name
        if tag_id == 0:
            userTag = UserTag()
        else:
            userTag = UserTag.objects.get(ID=tag_id)
        userTag.Name = name
        userTag.Description = desc
        if not userTag.Rules:
            userTag.Rules = rules
        userTag.UnionID = unionid
        userTag.NickName = nickname
        if not userTag.TagType:
            userTag.TagType = 'normal'
        userTag.Updated = datetime.datetime.now()
        userTag.save()
        updateVar('UserTag')
        return HttpResponse('ok')
    except Exception,e:
        Log("UpdateTag error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse("保存失败，请换名称再试")
    
@csrf_exempt
def DeleteTag(request):
    params = request.POST
    try:
        tag_id = int(params.get('id'))
        #to do 删除所有用户上的这个标签
        userTag = UserTag.objects.get(ID=tag_id)
        userTag.delete()
        updateVar('UserTag')
        return HttpResponse('ok')
    except Exception,e:
        Log("UpdateTag error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)

@csrf_exempt
def SetUserTags(request):
    #updateVar('UserTag')
    params = request.POST
    try:
        user_ids = params.get('users').split(',')
        tag_ids = params.get('tags').split(',')
        users = User.objects.filter(ID__in=user_ids)
        setUsersTags(users, tag_ids)
        return HttpResponse('ok')
    except Exception,e:
        Log("SetUserTags error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def setUsersTags(users, tag_ids):
        for user in users:
            user_tags = []
            if user.TagIDs:
                user_tags = user.TagIDs.split(',')
            need_update = False
            for tag_id in tag_ids:
                if tag_id not in user_tags:
                    need_update = True
            if need_update:
                arr = set(tag_ids + user_tags)
                arrStr = sorted([str(x) for x in arr])
                user.TagIDs = ",".join(arrStr)
                user.save()

    
@csrf_exempt    
def SetConditionTag(request):
    #updateVar('UserTag')
    params = request.POST
    try:
        Log("SetConditionTag params: %s" % params, "local", "0.0.0.0", "DEBUG")
        is_auto = params.get('is_auto')
        tag_type = 'normal'
        rule = ''
        if is_auto == 'true':
            tag_type='auto'
        rules = {}
        rules['mobile'] = params.get('mobile')
        rules['channel'] = params.get('channel')
        rules['is_new'] = params.get('is_new')
        lesson_ids = params.getlist('lesson_id[]')
        rules['lesson_ids'] = (',').join(lesson_ids)
        non_lesson_ids = params.getlist('non_lesson_id[]')
        rules['non_lesson_ids'] = (',').join(non_lesson_ids)
        rules['lesson_count'] = params.get('lesson_count')
        rules['associated'] = params.get('associated')
        rules['startDate'] = params.get('startDate')
        rules['endDate'] = params.get('endDate')
        rules['tag_ids'] = params.get('tag_ids')
        rule = json.dumps(rules)
        name = params.get('name')
        desc = params.get('desc')
        unionid = params.get('unionid')
        wx_user = wxUser.objects.filter(unionID=unionid)
        nickname = ''
        if wx_user:
            nickname = wx_user[0].Name
        u = UserTag(Name=name, Description = desc, Rules= rule, TagType=tag_type, UnionID = unionid, NickName=nickname)
        u.save()
        updateVar("UserTag")
        
        u = UserTag.objects.get(Name = name)
        
        tag_id = u.ID
        is_auto = params.get('is_auto')
        users = student_views.getStudents(params)
        tag_ids = []
        tag_ids.append(tag_id)
        setUsersTags(users,tag_ids)
        return HttpResponse('ok')
    except Exception,e:
        Log("SetUserTags error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
def AutoTags(request):
    try:
        tags = UserTag.objects.filter(TagType='auto')
        if tags:
            for tag in tags:
                users = student_views.getStudents(json.loads(tag.Rules))
                tag_ids = []
                tag_ids.append(tag.ID)
                setUsersTags(users,tag_ids)
        return HttpResponse('ok')
    except Exception,e:
        Log("autoTags error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def DeleteUserTags(request):
    #updateVar('UserTag')
    params = request.POST
    try:
        user_ids = params.get('users').split(',')
        tag_ids = params.get('tags').split(',')
        users = User.objects.filter(ID__in=user_ids)
        for user in users:
            user_tags = []
            if user.TagIDs:
                user_tags = user.TagIDs.split(',')
            for tag_id in tag_ids:
                if tag_id in user_tags:
                    user_tags.remove(tag_id);
            arrStr = sorted([str(x) for x in user_tags])
            user.TagIDs = ",".join(arrStr)
            user.save()
        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteUserTags error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)