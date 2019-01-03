from models import *
import traceback
import base64
import utils



class wxUserClass():
    
    def __init__(self, appid, userid):
        #self.tsaiObj = tsaiPlatform.tsaiPlatform()
        #Log(userinfo)
        try:
            obj = wxUser.objects.filter(openID = userid)
            if obj:
                self.wxUserData = obj[0]
                utils.Log("User found! %s" % userid)
            else:
                self.wxUserData = wxUser(openID = userid, SourceAccount = appid)   
                utils.Log("User created! %s" % userid)
                #self.wxUserData.save()
        except Exception, e:
            utils.Log( "Couldn't do wxUserClass __init__: %s" % e) 
        
        
    def SetUserInfo(self,userinfo):
        try:
            #utils.Log("SetUserInfo %s" % userinfo, Type="DEBUG")
            if ("headimgurl" in userinfo.keys()):
                self.wxUserData.Avatar = userinfo["headimgurl"]
            if ("avatarUrl" in userinfo.keys()):
                self.wxUserData.Avatar = userinfo["avatarUrl"]
            if ("sex" in userinfo.keys()):
                self.wxUserData.Gender = userinfo["sex"]
            if ("gender" in userinfo.keys()):
                self.wxUserData.Gender = userinfo["gender"]
            if ("User" in userinfo.keys()):
                self.wxUserData.Role = "User"
            if ("country" in userinfo.keys()):
                self.wxUserData.Country = userinfo["country"]
            if ("province" in userinfo.keys()):
                self.wxUserData.Province = userinfo["province"]
            if ("city" in userinfo.keys()):
                self.wxUserData.City = userinfo["city"]
            if ("unionid" in userinfo.keys()):
                self.wxUserData.unionID = userinfo["unionid"]
            if ("subscribe" in userinfo.keys()):
                self.wxUserData.Subscribed = userinfo["subscribe"]
            if ("nickname" in userinfo.keys()):
                utils.Log( userinfo["nickname"].encode('utf-8', 'ignore'))
                self.wxUserData.Name = userinfo["nickname"].encode('utf-8', 'ignore')
            if ("nickName" in userinfo.keys()):
                utils.Log( userinfo["nickName"].encode('utf-8', 'ignore'))
                self.wxUserData.Name = userinfo["nickName"].encode('utf-8', 'ignore')
            self.wxUserData.Updated = datetime.datetime.now()
            self.wxUserData.save()
        except Exception, e:
            utils.Log("SetUserInfo Error: %s" %e, Type="DEBUG")
            #self.wxUserData.save()
        return self.wxUserData
        
    def SetUserInfoWithPublicAppID(self,userinfo,publicAppID):
        if (publicAppID != ''):
            self.wxUserData.PublicAppID = publicAppID
            self.wxUserData.Role = "Admin"
        self.SetUserInfo(userinfo)
    
    def Subscribe(self):
        #utils.Log("Subscribe ", Type="DEBUG")
        self.wxUserData.Subscribed = 1
        self.wxUserData.save()
    
    def UnSubscribe(self):
        #utils.Log("UnSubscribe 1", Type="DEBUG")
        if self.wxUserData.ID:
            self.wxUserData.Subscribed = 0
            self.wxUserData.save()
        else:
            obj = wxUser.objects.filter(openID = self.wxUserData.openID)
            if obj:
                self.wxUserData = obj[0]
                obj[0].Subscribed = 0
                obj[0].save()
                
                