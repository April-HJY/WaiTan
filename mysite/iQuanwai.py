from utils import *

GetOpenidFromQuwanwai(usernumber):
    try:
        url = "https://www.confucius.mobi/rise/b/get/openid"
        values = {"memberid": usernumber}
        res = Post(url, values)
        return res
        
    except Exception, e:
        Log("GetOpenidFromQuwanwai Error :%s" % e)
        return None
            