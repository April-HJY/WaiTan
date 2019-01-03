#coding: utf-8
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.http import *
from utils import *
from wxUtils import *
from django.views.decorators.csrf import csrf_exempt  
from itertools import *
from utils2 import *
from mem_db_sync import *
import urllib
import urllib2
import json
import httplib
import mimetypes

def MiniappCampaignPage(request):
    template = loader.get_template('miniappcampaignpage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context))


def GetMiniappCampaignBanner(request):
    banners = getVar("MiniappCampaignBanner")
    banner_url=banners[0].URL
    return HttpResponse(banner_url)


@csrf_exempt
def SaveMiniappCampaignBanner(request):
    try:
        params = request.POST
        url = params.get('url','')
        if url:
            banners = getVar("MiniappCampaignBanner")
            banners[0].URL = url
            banners[0].save()
            updateVar("MiniappCampaignBanner")
        return HttpResponse('ok')
    except Exception,e:
        Log("SaveMiniappCampaignBanner error: %s" % e, Type="DEBUG")
        return HttpResponse('e')

def GetMiniappCampaignTags(request):
    try:
        tags = getVar("MiniappCampaignTags")
        tag_list = []
        for tag in tags:
            edit = "<a href='javascript:edit_tag(%d)'>修改</a>&nbsp;<a href='javascript:edit_lesson(%d)'>课程</a>&nbsp;<a href='javascript:delete_tag(%d)'>删除</a>" % (tag.ID,tag.ID,tag.ID)
            tag_list.append({"ID":tag.ID, "Name": tag.Name, "ChildName": tag.ChildName, "IsSpecial": tag.IsSpecial, "Order": tag.Order, "Edit": edit})
        return HttpResponse(json.dumps(tag_list))
    except Exception, e:
        Log("GetMiniappCampaignTags error: %s" % e, Type="DEBUG")
        return HttpResponse(jsonj.dumps([]))
    
    
@csrf_exempt
def DeleteMiniappCampaignTag(request):
    try:
        params = request.POST
        tag_id = int(params.get("tag_id",0))
        if not tag_id:
            return HttpResponse(json.dumps([]))

        tag = MiniappCampaignTags.objects.get(ID=tag_id)
        tag.delete()
        tag_product = MiniappCampaignTagProduct.objects.filter(CampaignTagID=tag_id)
        for prod in tag_product:
            prod.delete()
        updateVar("MiniappCampaignTags")
        updateVar("MiniappCampaignTagProduct")
        return HttpResponse('ok')
    except Exception, e:
        Log("DeleteMiniappCampaignTag error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def UpdateMiniappCampaignTags(request):
    try:
        params = request.POST
        tag_id = int(params.get("id",0))
        name = params.get("name",'')
        childname = params.get("childname",'')
        order = params.get("order",0)
        updated=datetime.datetime.now()
        if tag_id:
            tag = MiniappCampaignTags.objects.get(ID=tag_id)
            tag.Name = name
            tag.ChildName = childname
            tag.Order = order
            tag.Updated = updated
            tag.save()
        else:
            tag = MiniappCampaignTags(Name = name, ChildName = childname, Order = order)
            tag.save()
        updateVar("MiniappCampaignTags")
        return HttpResponse('ok')
    except Exception, e:
        Log("UpdateMiniappCampaignTags error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
def GetMiniappCampaignTagProducts(request):
    try:
        params = request.GET
        tag_id = params.get("tag_id",0)
        if not tag_id:
            return HttpResponse(json.dumps([]))
        else:
            tag_id = int(tag_id)
        tag_product = getVar("MiniappCampaignTagProduct")
        mini_product = getVar("MiniappProduct")
        product_list=[]
        for tag_prod in tag_product:
                product = None
                for mini_prod in mini_product:
                    if tag_prod.CampaignTagID == tag_id and mini_prod.ID == tag_prod.MiniProductID:
                        product = mini_prod
                        break;
                if product:
                    edit = "<a href='javascript:delete_lesson(%d)'>删除</a>" % (product.ID)
                    product_list.append({"ID":product.ID,"Name":product.Name,"Edit":edit})
        return HttpResponse(json.dumps(product_list))
    except Exception, e:
        Log("GetMiniappCampaignTags error: %s" % e, Type="DEBUG")
        return HttpResponse(jsonj.dumps([]))
    
    
def GetMiniappCampaignTagNewProducts(request):
    try:
        params = request.GET
        tag_id = params.get("tag_id",0)
        content = params.get("content",'')
        if not tag_id:
            return HttpResponse(json.dumps([]))
        else:
            tag_id = int(tag_id)
        #已有的过滤掉
        tag_product = getVar("MiniappCampaignTagProduct")
        product_ids = []
        for tag_p in tag_product:
            product_ids.append(tag_p.MiniProductID)
        mini_product = getVar("MiniappProduct")
        if content:
            mini_product = mini_product.filter(Name__contains=content, IsDisplay=1)
        else:
            mini_product = mini_product.filter(IsDisplay=1)
        product_list=[]
        for product in mini_product:
                if product.ID not in product_ids:
                    edit = "<a href='javascript:add_lesson(%d)'>关联</a>" % (product.ID)
                    product_list.append({"ID":product.ID,"Name":product.Name,"Edit":edit})
        return HttpResponse(json.dumps(product_list))
    except Exception, e:
        Log("GetMiniappCampaignTags error: %s" % e, Type="DEBUG")
        return HttpResponse(jsonj.dumps([]))
    
@csrf_exempt
def AddMiniappCampaignTagProducts(request):
    try:
        params = request.POST
        tag_id = int(params.get("tag_id",0))
        product_id = int(params.get("product_id",0))
        if not tag_id or not product_id:
            return HttpResponse(json.dumps([]))

        #已有的过滤掉
        tag_product = getVar("MiniappCampaignTagProduct")
        product_ids = []
        for tag_p in tag_product:
            product_ids.append(tag_p.MiniProductID)
        if product_id not in product_ids:
            m = MiniappCampaignTagProduct(CampaignTagID=tag_id, MiniProductID=product_id)
            m.save()
        updateVar("MiniappCampaignTagProduct")
        return HttpResponse('ok')
    except Exception, e:
        Log("AddMiniappCampaignTagProducts error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def DeleteMiniappCampaignTagProducts(request):
    try:
        params = request.POST
        tag_id = int(params.get("tag_id",0))
        product_id = int(params.get("product_id",0))
        if not tag_id or not product_id:
            return HttpResponse(json.dumps([]))

        m = MiniappCampaignTagProduct.objects.filter(CampaignTagID=tag_id, MiniProductID=product_id)
        if m:
            m[0].delete()
        updateVar("MiniappCampaignTagProduct")
        return HttpResponse('ok')
    except Exception, e:
        Log("DeleteMiniappCampaignTagProducts error: %s" % e, Type="DEBUG")
        return HttpResponse(e)
    
    
    
    