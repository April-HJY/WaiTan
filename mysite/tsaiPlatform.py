from wxUtils import *
import wxAccountInterface  
from Consts import *

class tsaiPlatform:
    def __init__(self):
        self.appId =  "wx75d48dcb77431c72"
        self.appSecret = "4b2f09cc3e1ebb4b8dd666f1f80c0db8"

    def GetAccessToken(self): # get component access token
        if (mc.get("component_access_token") is not None and mc.get("component_access_token_expired") is not None and mc.get("component_access_token_expired") > datetime.now()):
            Log("Componnet token expired:%s" % mc.get("component_access_token_expired"))
            Log("Ticket:%s"% mc.get("ComponentVerifyTicket") )
            return mc.get("component_access_token")
        try:
            url = "https://api.weixin.qq.com/cgi-bin/component/api_component_token" 
        
            #url = "http://applinzi.ddianke.com/deny"
            values ={
"component_verify_ticket": mc.get("ComponentVerifyTicket") ,
"component_appsecret": self.appSecret, 
"component_appid": self.appId 
}
            Log("GetAccessToken Started!")
            res = Post(url, values) 
            component_access_token = json.loads(res)["component_access_token"]
            expires_in = json.loads(res)["expires_in"]
            component_access_token_expired = datetime.now() + timedelta(0, expires_in , 0)
            Log("AccessToken: %s will be expired in : %s"% (component_access_token,component_access_token_expired) )
        
            mc.set("component_access_token", component_access_token)
            mc.set("component_access_token_expired", component_access_token_expired )
            return component_access_token
        except Exception, e:
            Log("Error when GetAccessToken: %s" % e, Type="DEBUG")
            return None


    
    def GetPreAuthCode(self):
    
    #if (mc.get("pre_auth_code") is not None and mc.get("pre_auth_code_expired") is not None and mc.get("pre_auth_code_expired") > datetime.datetime.now()):
    #        return mc.get("pre_auth_code")
             
        try:
            token = self.GetAccessToken()
            if (token is None):
                token = self.GetAccessToken()
            url = "https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode?component_access_token=" + token
            #url = "http://applinzi.ddianke.com/deny"
            #appid = "wx60072069c7fc883d"
            values = {
                  "component_appid": self.appId 
                  }
            res = Post(url, values)
            Log("Result:%s"%res)
            pre_auth_code = json.loads(res)["pre_auth_code"]
            expires_in = json.loads(res)["expires_in"]
            pre_auth_code_expired = datetime.now() + timedelta(0, expires_in , 0)
            Log("pre_auth_code: %s will be expired in %s" % (pre_auth_code, pre_auth_code_expired))
            mc.set("pre_auth_code", pre_auth_code)
            mc.set("pre_auth_code_expired", pre_auth_code_expired )
            return pre_auth_code
        
        except Exception, e:
            Log("Error when GetPreAuthCode: %s" %e, Type="DEBUG")
            return ""

    def GetAuthInfo(self,strAuthCode):
    
        try:
            token = self.GetAccessToken()
            url = "https://api.weixin.qq.com/cgi-bin/component/api_query_auth?component_access_token=%s"%token
            values = {
"component_appid":self.appId ,
"authorization_code": strAuthCode
                  }
            Log("GetAuthInfo Started!")
            res = Post(url, values)
            Log("Result:%s"%res)
            authorization_info = json.loads(res)["authorization_info"]
            authorizer_appid = authorization_info["authorizer_appid"]
            authorizer_access_token = ""
            authorizer_refresh_token = ""
            wxObj = wxAccountInterface.wxAccountInterface(authorizer_appid) 
            wxObj.UpdateAuthinfo(authorization_info)
            return wxObj
        except Exception, e:
            Log("Error when GetAuthInfo: %s" %e)
            return None
    

            

    def GetUserInfo(self, openid):
        try:
            accesstoken = self.GetAccessToken()
            url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (accesstoken, openid)
            response = urllib2.urlopen(url) 
            res = response.read().decode("utf8") 
            Log(res)
            return json.loads(res)
        except Exception, e:
            Log("Error when GetUserInfo: %s" % e)
            return None
        
    def GetwxAccountInterface(self, authorizer_appid):
    	try:
            wxObj = wxAccountInterface.wxAccountInterface(authorizer_appid)
            return wxObj
        except Exception, e:
            Log("Error when GetwxAccountInterface: %s" %e)
            return None
            
