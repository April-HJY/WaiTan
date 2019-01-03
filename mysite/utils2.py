from utils import *

def RefreshMarathon():
    try:
        
        allMarathon = Sheet1.objects.all()
        for c in allMarathon:
            try:
                if (c.website is not None):
                    url = c.website
                    response = urllib2.urlopen(url) 
                    lastmodified = response.headers.get("Last-Modified")
                    Log("URL:%s, last modified: %s"% (url,lastmodified))
                    if (lastmodified is not None):
                        c.LastModified = lastmodified
                        c.save()
                    else:
                        pagesize = len(response.read().decode("utf8"))
                        if (pagesize!=c.PageSize):
                            c.PageSize = pagesize
                            c.LastModified = datetime.datetime.now()
                            c.save()
            except Exception, e:
                c.LastModified = "Error: %s" % e
                
        return ""
    except Exception, e:
        Log("RefreshMarathon Error!%s" % e)