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

def ProductPage(request):
    template = loader.get_template('productpage.html')
    context = RequestContext(request, {"Info":("ticket")})
    return HttpResponse(template.render(context)) 


def GetProductTypes(request):
    try:
        params = request.GET
        res = []
        product_types = getVar("ProductType")
        for product_type in product_types:
            res.append({"Name":product_type.Name, "ID": product_type.ID})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetProductType error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)


def GetProducts(request):
    try:
        params = request.GET
        Log("GetProducts params: %s" % params, "local", "0.0.0.0", "DEBUG")
        res = []
        condition = params.get('condition')
        products = getVar("Product")
        channel_dic = GetChannelRemarkDic()
        #if condition:
        #    products = products.filter(ProductName__contains=condition)
        for product in products:
            edit = "<a href='javascript:putaway_product(%d)'>上架</a>&nbsp;<a href='javascript:edit_product(%d)'>修改</a>&nbsp;<a href='javascript:delete_product(%d)'>删除</a>" % (product.ID,product.ID,product.ID)
            if product.PutawayChannels:
                edit += "&nbsp;<a href='javascript:takeoff_product(%d)'>下架</a>" % product.ID
            putaway_channels = []
            if product.PutawayChannels:
                putaway_channel_ids = product.PutawayChannels.split(',')
                for channel_id in putaway_channel_ids:
                    putaway_channels.append(channel_dic[int(channel_id)])
            messages = ProductMessage.objects.filter(ProductID = product.ID)
            msg = []
            for message in messages:
                msg.append({"message_id":message.ID,"message_name":message.Name, "message_type_id": message.ProductMessageTypeID})
            relation = ProductAndProductTag.objects.values("ProductTagID").filter(ProductID = product.ID)
            tag_ids = []
            for r in relation:
                tag_ids.append(r['ProductTagID'])
            
            skus = []
            if product.SKUName:
                skus = json.loads(product.SKUName)
            res.append({"ID":product.ID,"ProductName":product.ProductName, "ProductCode": product.ProductCode, "SKUs": skus, "Price": product.Price, 
                        "ProductUrl1": product.ProductUrl1, "ProductUrl2": product.ProductUrl2, "ProductUrl3": product.ProductUrl3, "ProductUrl4": product.ProductUrl4,
                        "ProductUrl5": product.ProductUrl5, "ProductUrl6": product.ProductUrl6, "ProductUrl7": product.ProductUrl7, "ProductUrl8": product.ProductUrl8, "ProductUrl9": product.ProductUrl9,
                        "ProductUrl10": product.ProductUrl10, "ProductUrl11": product.ProductUrl11, "Inventory": product.Inventory, "PutawayChannels": ','.join(putaway_channels), 
                        "ShareDescription":product.ShareDescription, "HotPoint":product.HotPoint,"OriginalPrice":product.OriginalPrice,"CostPrice":product.CostPrice,"Messages":msg,
                        "ProductTypeID":product.ProductTypeID,"LessonCategoryID":product.LessonCategoryID, "Edit":edit, 'tag_ids':tag_ids,"ProductProperties":product.ProductProperties,
                        "TeacherDesc":product.TeacherDesc, "Order":product.Order, "SetSKU":product.SetSKU, "DistributePoint":product.DistributePoint, "DistributeCashback":product.DistributeCashback, 
                        "PointLimit":product.PointLimit, "PriceDisplay": product.Price/100.0,"OriginalPriceDisplay":product.OriginalPrice/100.0,"CostPriceDisplay":product.CostPrice/100.0})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetProducts error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetProductPutawayChannels(request):
    try:
        params = request.GET
        Log("GetProductPutawayChannels params: %s" % params, "local", "0.0.0.0", "DEBUG")
        product_id = params.get('product_id')
        product = Product.objects.get(ID=product_id)
        putaway_channels = product.PutawayChannels.split(',')
        channelDic = GetChannelRemarkDic()
        res = []
        for channel in putaway_channels:
            res.append({"Name":channelDic[int(channel)], "Key": int(channel)})
        Log("GetProductPutawayChannels res: %s" % res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetProductPutawayChannels error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def TakeOffProduct(request):
    try:
        params = request.POST
        Log("TakeOffProduct params: %s" % params, "local", "0.0.0.0", "DEBUG")
        product_id = params.get('product_id')
        channel_id = params.get('channel_id')
        set_sku = params.get('set_sku', False)
        res = 'ok'
        if int(channel_id) == 15:
            product = Product.objects.get(ID=product_id)
            miniapp_product = MiniappProduct.objects.filter(ProductID=product_id)
            putaway_channels = product.PutawayChannels
            channels = [ int(x) for x in putaway_channels.split(',')]
            channels.remove(15)
            product.PutawayChannels = ','.join(channels)
            product.save()
            if miniapp_product:
                miniapp_product = miniapp_product[0]
                miniapp_product.IsDisplay = 0
                miniapp_product.save()
        updateVar('MiniappProduct')
        updateVar('Product')
        Log("TakeOffProduct res: %s" % res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(res)
    except Exception, e:
        Log("TakeOffProduct error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def PutawayProduct(request):
    try:
        params = request.POST
        Log("PutawayProduct params: %s" % params, "local", "0.0.0.0", "DEBUG")
        product_id = params.get('product_id')
        channel_id = params.get('channel_id')
        set_sku = params.get('set_sku', False)
        res = ''
        if int(channel_id) == 15:
            res = PutawayMiniapp(product_id,channel_id,set_sku)
        Log("PutawayProduct res: %s" % res, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(res)
    except Exception, e:
        Log("PutawayProduct error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def PutawayMiniapp(product_id,channel_id,set_sku):
    try:
        product = Product.objects.get(ID=product_id)
        if set_sku=='true':
            product.SetSKU = 1
        else:
            product.SetSKU = 0
        miniapp_product = MiniappProduct.objects.filter(ProductID=product_id)
        if miniapp_product:
            miniapp_product = miniapp_product[0]
            miniapp_product.Name = product.ProductName
            miniapp_product.ProductTypeID = product.ProductTypeID
            miniapp_product.LessonCategoryID = product.LessonCategoryID
            miniapp_product.ProductUrl1 = product.ProductUrl1
            miniapp_product.ProductUrl2 = product.ProductUrl2
            miniapp_product.ProductUrl3 = product.ProductUrl3
            miniapp_product.ProductUrl4 = product.ProductUrl4
            miniapp_product.ProductUrl5 = product.ProductUrl5
            miniapp_product.ProductUrl6 = product.ProductUrl6
            miniapp_product.ProductUrl7 = product.ProductUrl7
            miniapp_product.ProductUrl8 = product.ProductUrl8
            miniapp_product.ProductUrl9 = product.ProductUrl9
            miniapp_product.ProductUrl10 = product.ProductUrl10
            miniapp_product.ProductUrl11 = product.ProductUrl11
            miniapp_product.Order = product.Order
            miniapp_product.SKUName = product.SKUName
            miniapp_product.Price = product.Price
            miniapp_product.OriginalPrice = product.OriginalPrice
            miniapp_product.Inventory = product.Inventory
            miniapp_product.CostPrice = product.CostPrice
            miniapp_product.DistributePoint = product.DistributePoint
            miniapp_product.DistributeCashback = product.DistributeCashback
            miniapp_product.PointLimit = product.PointLimit
            miniapp_product.Messages = product.Messages
            miniapp_product.ProductProperties = product.ProductProperties
            miniapp_product.TeacherDesc = product.TeacherDesc
            miniapp_product.IsDisplay = 1
            miniapp_product.Updated = datetime.datetime.now()
            miniapp_product.save()
            #product.PutawayChannels
        else:
            miniapp_product = MiniappProduct(ProductID=product.ID,Code='miniapp_product',Name = product.ProductName,ProductTypeID = product.ProductTypeID,ProductUrl1 = product.ProductUrl1,
                                            ProductUrl2 = product.ProductUrl2, ProductUrl3 = product.ProductUrl3, ProductUrl4 = product.ProductUrl4, ProductUrl5 = product.ProductUrl5,
                                            ProductUrl6 = product.ProductUrl6, ProductUrl7 = product.ProductUrl7, ProductUrl8 = product.ProductUrl8, ProductUrl9 = product.ProductUrl9,
                                            ProductUrl10 = product.ProductUrl10, ProductUrl11 = product.ProductUrl11, Order = product.Order, DistributePoint = product.DistributePoint, 
                                            DistributeCashback = product.DistributeCashback, PointLimit = product.PointLimit, SKUName = product.SKUName,Price = product.Price,OriginalPrice = product.OriginalPrice,
                                            Inventory = product.Inventory,CostPrice = product.CostPrice, Messages = product.Messages,LessonCategoryID = product.LessonCategoryID,
                                            ProductProperties = product.ProductProperties,TeacherDesc = product.TeacherDesc,IsDisplay = 1)
            miniapp_product.save()
        putaway_channels = product.PutawayChannels
        if putaway_channels:
            channels = putaway_channels.split(',')
            if channel_id not in channels:
                channels.append(channel_id)
            putaway_channels = ','.join(channels)
        else:
            putaway_channels = channel_id
        product.PutawayChannels = putaway_channels    
        product.save()
        #上架到导入表
        thirdparty = LessonsOfThirdParty.objects.filter(ProductID=product.ID,ChannelID=channel_id)
        skus = json.loads(product.SKUName)
        if set_sku=='true' and skus:
            sku_group_list = []
            for sku in skus:
                sku_list = []
                sku_group_list.append(sku_list)
                for sku_value in sku['sku_values']:
                    sku_list.append("%s:%s" % (sku['sku_name'],sku_value['sku_value']))
                    
            sku_list = []
            
            for sku_group in sku_group_list:
                sku_times = len(sku_group)
                temp_sku_list = []
                if sku_list:                  
                    for sku in sku_list:
                        for sku2 in sku_group:
                            temp_sku_list.append("%s;%s" % (sku,sku2))
                    sku_list = temp_sku_list
                else:
                    for sku in sku_group:
                        sku_list.append(sku)

            #Log("PutawayProduct sku_list:%s"%sku_list, "local", "0.0.0.0", "DEBUG")
            #先删除没有sku的课程
            if thirdparty:
                for thirdparty_lesson in thirdparty:
                    if not thirdparty_lesson.SKUName:
                        thirdparty_lesson.delete()
            #再判断是否sku修改过
            thirdparty = LessonsOfThirdParty.objects.filter(ProductID=product.ID,ChannelID=channel_id)
            thirdparty_usedids = []
            if thirdparty:
                for thirdparty_lesson in thirdparty:
                    if thirdparty_lesson.SKUName in sku_list:
                        thirdparty_usedids.append(thirdparty_lesson.ID)
                        sku_list.remove(thirdparty_lesson.SKUName)
                        thirdparty_lesson.Name = product.ProductName
                        thirdparty_lesson.LessonCategoryID = product.LessonCategoryID
                        thirdparty_lesson.save()
                for thirdparty_lesson in thirdparty:
                    if thirdparty_lesson.ID not in thirdparty_usedids:
                        thirdparty_lesson.delete()
            for sku in sku_list:
                if sku:
                    thirdparty = LessonsOfThirdParty(ProductID=product.ID,ChannelID=channel_id,Name = product.ProductName,SKUName=sku,LessonCategoryID = product.LessonCategoryID,TelMsgTemplateID=0)
                    thirdparty.save()
                        
        else:
            if thirdparty:
                for thirdparty_lesson in thirdparty:
                    if thirdparty_lesson.SKUName:
                        thirdparty_lesson.delete()
            thirdparty = LessonsOfThirdParty.objects.filter(ProductID=product.ID,ChannelID=channel_id)
            if thirdparty:
                thirdparty = thirdparty[0]
                thirdparty.Name = product.ProductName
                thirdparty.LessonCategoryID = product.LessonCategoryID
                thirdparty.save()
            else:
                thirdparty = LessonsOfThirdParty(ProductID=product.ID,ChannelID=channel_id,Name = product.ProductName,SKUName=None,LessonCategoryID = product.LessonCategoryID,TelMsgTemplateID=0)
                thirdparty.save()
        updateVar('LessonsOfThirdParty')
        updateVar('MiniappProduct')
        updateVar('Product')
        return 'ok'
    except Exception, e:
        Log("PutawayProduct error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return e
    

@csrf_exempt
def SaveProduct(request):
    try:
        params = request.POST
        Log("SaveProduct params: %s" % params, "local", "0.0.0.0", "DEBUG")
        update_id = params.get('id', None)
        product_type_id = params.get('product_type_id')
        category_id = params.get('category_id',0)
        product_name = params.get('product_name')
        product_url1 = params.get('product_url1', '')
        product_url2 = params.get('product_url2', '')
        product_url3 = params.get('product_url3', '')
        product_url4 = params.get('product_url4', '')
        product_url5 = params.get('product_url5', '')
        product_url6 = params.get('product_url6', '')
        product_url7 = params.get('product_url7', '')
        product_url8 = params.get('product_url8', '')
        product_url9 = params.get('product_url9', '')
        product_url10 = params.get('product_url10', '')
        product_url11 = params.get('product_url11', '')
        share_description = params.get('share_description', '')
        hot_point = params.get('hot_point', '')
        sku_name = params.get('sku_name', '')
        product_prop = params.get('product_prop', '')
        teacher_desc = params.get('teacher_desc', '')
        price = params.get('price', 0)
        if price:
            price = int(price)
        else:
            price = 0
        
        original_price = params.get('original_price', 0)
        if original_price:
            original_price = int(original_price)
        else:
            original_price = 0
            
        inventory = params.get('inventory', 0)
        if inventory:
            inventory = int(inventory)
        else:
            inventory = 0
            
        cost_price = params.get('cost_price', 0)
        if cost_price:
            cost_price = int(cost_price)
        else:
            cost_price = 0
        
        order = params.get('order', 0)
        if order:
            order = int(order)
        else:
            order = 0
            
        distribute_point = params.get('distribute_point', 0)
        if distribute_point:
            distribute_point = int(distribute_point)
        else:
            distribute_point = 0
            
        distribute_cashback = params.get('distribute_cashback', 0)
        if distribute_cashback:
            distribute_cashback = int(distribute_cashback)
        else:
            distribute_cashback = 0
            
        point_limit = params.get('point_limit', 0)
        if point_limit:
            point_limit = int(point_limit)
        else:
            point_limit = 0
        
        messages = params.get('messages', '')
        if messages:
            messages = json.loads(messages)
        tag_ids = params.get('tag_ids', '')
        if tag_ids:
            tag_ids = json.loads(tag_ids)
        product = None
        if update_id:
            product = Product.objects.get(ID=update_id)
            product.ProductTypeID = product_type_id
            product.LessonCategoryID = category_id
            product.ProductName = product_name
            product.ProductUrl1 = product_url1
            product.ProductUrl2 = product_url2
            product.ProductUrl3 = product_url3
            product.ProductUrl4 = product_url4
            product.ProductUrl5 = product_url5
            product.ProductUrl6 = product_url6
            product.ProductUrl7 = product_url7
            product.ProductUrl8 = product_url8
            product.ProductUrl9 = product_url9
            product.ProductUrl10 = product_url10
            product.ProductUrl11 = product_url11
            product.ShareDescription = share_description
            product.HotPoint = hot_point
            product.SKUName = sku_name
            product.Price = price
            product.OriginalPrice = original_price
            product.Inventory = inventory
            product.CostPrice = cost_price
            product.DistributePoint = distribute_point
            product.DistributeCashback = distribute_cashback
            product.PointLimit = point_limit
            product.Messages = messages
            product.ProductProperties = product_prop
            product.TeacherDesc = teacher_desc
            product.Order = order
            product.save()
        else:
            product = Product(ProductTypeID=product_type_id, ProductName=product_name, ProductUrl1=product_url1, ProductUrl2=product_url2, ProductUrl3=product_url3, ProductUrl4=product_url4, 
                              ProductUrl5=product_url5, ProductUrl6=product_url6, ProductUrl7=product_url7, ProductUrl8=product_url8, ProductUrl9=product_url9, ProductUrl10=product_url10, ProductUrl11=product_url11, 
                              ShareDescription=share_description, HotPoint=hot_point, SKUName=sku_name, Price=price, OriginalPrice=original_price, Inventory=inventory, CostPrice=cost_price, Order=order, 
                              DistributePoint = distribute_point, DistributeCashback = distribute_cashback, PointLimit = point_limit, Messages=messages, LessonCategoryID = category_id,ProductProperties = product_prop,TeacherDesc = teacher_desc)
            product.save()
            
        #update_message
        Log("SaveProduct messages: %s" % messages, "local", "0.0.0.0", "DEBUG")
        product_id = product.ID
        old_messages = ProductMessage.objects.filter(ProductID = product_id)
        delete_list = []
        for message in old_messages:
            is_delete = True
            for m in messages:
                if message.ID == int(m['message_id']):
                    is_delete = False
                    message.Name = m['message_name']
                    message.ProductMessageTypeID = int(m['message_type_id'])
                    message.Updated = datetime.datetime.now()
                    message.save()
            if is_delete:
                delete_list.append(message)
        
        for m in messages:
            if int(m['message_id']) == 0:
                message = ProductMessage(ProductID = product_id, Name = m['message_name'], ProductMessageTypeID=int(m['message_type_id']))
                message.save()
        
        for d in delete_list:
            d.delete()
        
        #save_tags
        curr_tags = ProductAndProductTag.objects.filter(ProductID=product_id)
        remove_tags = []
        Log("SaveProduct curr_tags:%s"%curr_tags, "local", "0.0.0.0", "DEBUG")
        for curr_tag in curr_tags:
            curr_product_tag_id = int(curr_tag.ProductTagID)
            if curr_product_tag_id in tag_ids:
                tag_ids.remove(curr_product_tag_id)
            else:
                remove_tags.append(curr_tag)
        Log("SaveProduct tag_ids:%s"%tag_ids, "local", "0.0.0.0", "DEBUG")
        for tag_id in tag_ids:
            relation = ProductAndProductTag(ProductID=product_id, ProductTagID=tag_id)
            relation.save()
        for d in remove_tags:
            d.delete()
            
        updateVar("Product")
        updateVar("ProductMessage")
        updateVar("ProductAndProductTag")
        return HttpResponse('ok')
    except Exception,e:
        Log("SaveProduct error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
@csrf_exempt
def DeleteProduct(request):
    try:
        params = request.POST
        Log("DeleteProduct params: %s" % params, "local", "0.0.0.0", "DEBUG")
        delete_id = params.get('id', None)
        
        if delete_id:
            product = Product.objects.get(ID=delete_id)
            product.delete()
        return HttpResponse('ok')
    except Exception,e:
        Log("DeleteProduct error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetProductMessageTypes(request):
    try:
        params = request.GET
        Log("GetProductMessageTypes params: %s" % params, "local", "0.0.0.0", "DEBUG")
        res = []
        messages = getVar("ProductMessageType")
        for message in messages:
            #edit = "<a href='javascript:edit_teacher(%d)'>修改</a>&nbsp;<a href='javascript:delete_teacher(%d)'>删除</a>" % (teacher.ID,teacher.ID)
            res.append({"ID":message.ID,"Name":message.Name, "RegularExpression": message.RegularExpression, "InputType": message.InputType, "Placeholder": message.Placeholder})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetProductMessageTypes error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetProductMessages(request):
    try:
        params = request.GET
        Log("GetProductMessages params: %s" % params, "local", "0.0.0.0", "DEBUG")
        product_id = params.get('product_id', 0)
        res = []
        messages = ProductMessage.objects.filter(ProductID = product_id)
        for message in messages:
            #edit = "<a href='javascript:edit_teacher(%d)'>修改</a>&nbsp;<a href='javascript:delete_teacher(%d)'>删除</a>" % (teacher.ID,teacher.ID)
            res.append({"ID":message.ID,"Name":message.Name, "ProductMessageTypeID": message.ProductMessageTypeID})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetProductMessages error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetAllProductTags(request):
    try:
        params = request.GET
        tags = getVar("ProductTag")
        res = []
        for tag in tags:
            res.append({"ID":tag.ID,"Name":tag.Name, "FullName": tag.FullName, "Code": tag.Code})
        return HttpResponse(json.dumps(res))
    except Exception, e:
        Log("GetAllProductTags error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def SaveProductTags(request):
    try:
        #逻辑有误，没有移除被删掉的项
        params = request.POST
        product_id = params.get("product_id",0)
        tag_ids = params.get("tag_ids",'')
        tag_id_list = [int(i) for i in tag_ids.split(',')]
        curr_tags = ProductAndProductTag.objects.values("ProductTagID").filter(ProductID=product_id, ProductTagID__in=tag_id_list)
        Log("SaveProductTags curr_tags:%s"%curr_tags, "local", "0.0.0.0", "DEBUG")
        for curr_tag in curr_tags:
            curr_product_tag_id = int(curr_tag['ProductTagID'])
            if curr_product_tag_id in tag_id_list:
                tag_id_list.remove(curr_product_tag_id)
        Log("SaveProductTags tag_id_list:%s"%tag_id_list, "local", "0.0.0.0", "DEBUG")
        for tag_id in tag_id_list:
            relation = ProductAndProductTag(ProductID=product_id, ProductTagID=tag_id)
            relation.save()
        return HttpResponse('ok')
    except Exception, e:
        Log("SaveProductTags error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
@csrf_exempt
def DeleteProductTag(request):
    try:
        params = request.POST
        product_id = params.get("product_id",0)
        tag_id = params.get("tag_id",0)
        relation = ProductAndProductTag.objects.filter(ProductID=product_id, ProductTagID=tag_id)
        if relation:
            relation[0].delete()
        return HttpResponse('ok')
    except Exception, e:
        Log("DeleteProductTag error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return HttpResponse(e)
    
    
def GetProductTags(product_id):
    try:
        res = []
        relation = ProductAndProductTag.objects.values('ProductTagID').filter(ProductID = product_id)
        tag_ids = []
        for r in relation:
            tag_ids.append(r['ProductTagID'])
        tags = ProductTag.objects.filter(ID__in = tag_ids)
        for tag in tags:
            #edit = "<a href='javascript:edit_teacher(%d)'>修改</a>&nbsp;<a href='javascript:delete_teacher(%d)'>删除</a>" % (teacher.ID,teacher.ID)
            res.append({"ID":tag.ID,"Name":tag.Name, "FullName": tag.FullName, "Code": tag.Code})
        Log("GetProductTags res:%s"%res, "local", "0.0.0.0", "DEBUG")
        return res
    except Exception, e:
        Log("GetProductTags error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return e
    
    
def GetProductTagsByID(request):
        params = request.GET
        Log("GetProductTagsByID params: %s" % params, "local", "0.0.0.0", "DEBUG")
        product_id = params.get('product_id', 0)
        res = GetProductTags(product_id)
        return HttpResponse(json.dumps(res))
    
    
@csrf_exempt
def UpdateProductMessages(request):
    try:        
        params = request.POST
        Log("UpdateProductMessages params: %s" % params, Type="DEBUG")
        product_id = params.get('product_id', 0)
        messages = params.get('messages', '')
        if messages:
            messages = json.loads(messages)
        #Log("UpdateCourseLesson lessons: %s" % lessons, Type="DEBUG")
        
        old_messages = ProductMessage.objects.filter(ProductID = product_id)
        delete_list = []
        for message in old_messages:
            is_delete = True
            for m in messages:
                if message.ID == int(m['message_id']):
                    is_delete = False
                    message.Name = m['message_name']
                    message.ProductMessageTypeID = int(m['message_type_id'])
                    message.Updated = datetime.datetime.now()
                    message.save()
            if is_delete:
                delete_list.append(message)
        
        for m in messages:
            if int(m['message_id']) == 0:
                message = ProductMessage(ProductID = product_id, Name = m['message_name'], ProductMessageTypeID=int(m['message_type_id']))
                message.save()
        
        for d in delete_list:
            d.delete()
            
        updateVar("ProductMessage")
        return HttpResponse('ok')
    except Exception,e:
        Log("UpdateProductMessagesw error: %s" %e, Type="DEBUG")
        return HttpResponse(e)
    


    
    
    