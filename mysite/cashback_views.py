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
from django.db import transaction
import wxAccountInterface

def UpdateCashbackToUser(wxuser_id, amount, object_type='', object_id=0, reason=''):
    try:
        #Log("UpdateCashbackToUser", "local", "0.0.0.0", "DEBUG")
        detail = UserCashbackDetail.objects.filter(wxUserID = wxuser_id, Amount = amount, ObjectType = object_type, ObjectID = object_id, Reason = reason)
        if detail:
            #Log("UpdateCashbackToUser already update:%d %d %s %d %s" % (wxuser_id, point, object_type, object_id, reason), "local", "0.0.0.0", "DEBUG")
            return 'already update'
        else:
            detail = UserPointDetail(wxUserID = wxuser_id, Points = point, ObjectType = object_type, ObjectID = object_id, Reason = reason)
            detail.save()
        return 'ok'
    except Exception,e:
        Log("UpdateCashbackToUser error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return e
    
    
def GetUserCashbackAmount(openid):
    try:
        wxuser = wxUser.objects.get(openID = openid)
        details = UserCashbackDetail.objects.values('Amount').filter(wxUserID=wxuser.ID, IsHandled=0)
        amount = 0
        for detail in details:
            amount += detail['Amount']
        return amount
    except Exception,e:
        Log("Cashback GetUserCashbackAmount error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return 0
    
    
def AddCashbackToDistributor(buyer_openid, distributor_id, product_id, object_type='', object_id=0, reason=''):    
    try:
        #老用户标签是59
        old_user_tag_id = 59
        wxbuyer = wxUser.objects.get(openID = buyer_openid)
        buyer = User.objects.filter(Mobile=wxbuyer.Mobile)

        if buyer.TagIDs:
            tags = buyer.TagIds.split(',')
            if old_user_tag_id in tags:
                return 'not new user'
        product = MiniappProduct.objects.get(ID=product_id)
        if not product.DistributeCashback:
            return 'no cashback product'
        res = UpdateCashbackToUser(distributor_id, product.DistributeCashback, object_type, object_id, reason)
        return res
    except Exception,e:
        Log("Cashback AddCashbackToDistributor error: %s" % e, "local", "0.0.0.0", "DEBUG")
        return e
    

    
    
    
    