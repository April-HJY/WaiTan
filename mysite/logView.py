#coding: utf-8
from django.http import HttpResponse
from django.template import RequestContext, loader
import pylibmc as memcache
import urllib2
import urllib
import hashlib
import cookielib
from utils import *

mc = memcache.Client()


def md5(str):
    m = hashlib.md5()   
    m.update(str)
    return m.hexdigest()


def home(request):
    
#        try:
#            url = 'https://mp.weixin.qq.com/cgi-bin/login'
#            values = {'username' : 'tsaireader', 'pwd' : '5912d7bfd10f631f1715bf85bbb72d97', 'imgcode':'', 'f' : 'json' }  
#            data = urllib.urlencode(values)
#            http_header = {
#                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
#"X-Requested-With" : "XMLHttpRequest",
#"Referer" : "https://mp.weixin.qq.com/",
#"Accept-Language" : "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
#"Accept-Encoding" :	"gzip, deflate",
#"User-Agent" : "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; Touch; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; InfoPath.3)",
#"Host" : "mp.weixin.qq.com",
#"Content-Length" : "72",
#"DNT" : "1",
#"Connection" : "Keep-Alive",
#"Cache-Control" : "no-cache"
#}
#            req = urllib2.Request(url, data, http_header)
#            response = urllib2.urlopen(req) 
#            tempDoc = response.read().decode("utf8") 
#            LogInfo = tempDoc
#        except Exception, e:
#            LogInfo = e
        
        template = loader.get_template('logview.html')
        LogInfo = PageLog.objects.filter(LogType = "Debug").order_by("-ID")[0:200]
        if request.method == 'GET':
            params = request.GET
            if ("logtype" in params.keys()) and (params["logtype"] == "all"):
                LogInfo = PageLog.objects.order_by("-ID")[0:200]
        
        
        #+ mc.get("component_access_token")
        context = RequestContext(request, {"LogInfo":LogInfo})
        return HttpResponse(template.render(context))
    
def log(request):

        if request.method == 'GET':
            params = request.GET
            Log(params["LogInfo"])
        return  HttpResponse("OK")