import pylibmc as memcache
from models import *
from django.db.models import *
from utils import *

mc = memcache.Client()

def getVar(strVar):
    if (strVar not in mc):
        #Log("memcache Hit!")
        #return mc.get(strVar)
        updateVar(strVar)
    #else:
    #    if getExpireTime(strVar)  < datetime.datetime.now():
    #        updateVar(strVar)
    #updateVar(strVar)
    return mc.get(strVar)

      
def updateVar(strVar):
    
    if (strVar == 'miniappUser'):
        res = wxUser.objects.filter(SourceAccount = 'wx0c0e0edd8eaad932').order_by("ID")
    if (strVar == 'AllWxAcounts'):
        res = wxAccounts.objects.filter(Disabled = 0).order_by("-OnboardDate")
    if (strVar == 'wxUserCount'):
        res = wxAccounts.objects.filter(Disabled = 0).aggregate(Sum('UserCount'))["UserCount__sum"]
    if (strVar ==  'wxNewsCount'):
        res = wxAccounts.objects.all().aggregate(Sum('ProcessIndex'))["ProcessIndex__sum"]
    if (strVar.startswith('comments')):
        res =  Comment.objects.filter(ArticleID = strVar.lstrip("comments#"))
    if (strVar.startswith('article')):
        res =  Articles.objects.filter(ID = strVar.lstrip("article#"))
    if (strVar == 'LatestArticles'):
        res = Articles.objects.all().order_by("-PostDate")[0:9]
    if (strVar == 'HotArticles'):
        res = Articles.objects.all().order_by("-PostDate")[0:9]    
    if (strVar == 'Schedule'):
        res = Schedule.objects.filter(Expired = 0, ArticleType = '').order_by("-ScheduleDate")
    if (strVar == 'Topic'):
        res = Schedule.objects.filter(ArticleType = 'topic').order_by("-ISTop","-PostDate")
    if (strVar == 'Comment'):
        res = Schedule.objects.filter(ArticleType = 'comment').order_by("PostDate")
    if (strVar == 'CommunityArticles'):
        res = Schedule.objects.filter(Q(ArticleType = 'comment') | Q(ArticleType = 'topic')).order_by("ID")
    if (strVar == 'Role'): 
        res = Role.objects.all().order_by("ID")
    if (strVar == 'Authority'):
        res = Authority.objects.all().order_by("ID")
    if (strVar == 'AuthorityType'):
        res = AuthorityType.objects.all().order_by("ID")
    if (strVar == 'PaidArticles'):
        res = PaidArticles.objects.all().order_by("ID")
    if (strVar == 'Product'):
        res = Product.objects.all().order_by("-ID")
    if (strVar == 'ProductType'):
        res = ProductType.objects.all().order_by("ID")
    if (strVar == 'ProductMessageType'):
        res = ProductMessageType.objects.all().order_by("ID")
    if (strVar == 'ProductMessage'):
        res = ProductMessage.objects.all().order_by("ID")
    if (strVar == 'ProductTag'):
        res = ProductTag.objects.all().order_by("ID")
    if (strVar == 'ProductAndProductTag'):
        res = ProductAndProductTag.objects.all().order_by("ProductTagID")
    if (strVar == 'MiniappProduct'):
        res = MiniappProduct.objects.all().order_by("Order","-ID")
    if (strVar == 'MiniappTeacher'):
        res = MiniappTeacher.objects.all().order_by("ID")
    if (strVar == 'MiniappBanner'):
        res = MiniappBanner.objects.all().order_by("ID")
    if (strVar == 'MiniappCampaignBanner'):
        res = MiniappCampaignBanner.objects.all().order_by("ID")
    if (strVar == 'MiniappCashbackBanner'):
        res = MiniappCashbackBanner.objects.all().order_by("ID")
    if (strVar == 'MiniappCampaignTags'):
        res = MiniappCampaignTags.objects.all().order_by("Order","-ID")
    if (strVar == 'MiniappCampaignTagProduct'):
        res = MiniappCampaignTagProduct.objects.all().order_by("ID")
    if (strVar == 'OITM'):
        res = OITM.objects.all().order_by("ID")
    if (strVar == 'BusinessSpending'):
        res = BusinessSpending.objects.all().order_by("ID")
    if (strVar == 'wxProduct'):
        res = wxProduct.objects.all().order_by("ID")
    if (strVar == 'Channel'): 
        res = Channel.objects.all().order_by("ID")
    #if (strVar == 'User'): 
    #    res = User.objects.all().order_by("ID")
    #if (strVar == 'TradeInfo'): 
    #    res = TradeInfo.objects.all().order_by("ID")
    if (strVar == 'Lesson'): 
        res = Lesson.objects.all().order_by("ID")
    if (strVar == 'LessonsOfThirdParty'): 
        res = LessonsOfThirdParty.objects.all().order_by("ID")
    if (strVar == 'LessonsRelation'): 
        res = LessonsRelation.objects.all().order_by("ID")
    if (strVar == 'ImportDetail'): 
        res = ImportDetail.objects.all().order_by("-ID")
    if (strVar == 'TelMsgTemplate'): 
        res = TelMsgTemplate.objects.all().order_by("-ID")
    if (strVar == 'wxMsgTemplate'): 
        res = wxMsgTemplate.objects.all().order_by("-ID")
    if (strVar == 'UserTag'): 
        res = UserTag.objects.all().order_by("ID")
    if (strVar == 'Campaign'): 
        res = Campaign.objects.all().order_by("-ID")
    if (strVar == 'UserCampaign'): 
        res = UserCampaign.objects.all().order_by("-ID")
    if (strVar == 'Coupons'): 
        res = Coupons.objects.all().order_by("-Created")
    if (strVar == 'question_answer'): 
        res = question_answer.objects.all().order_by("ID")
    if (strVar == 'CloudCourse'):
        res = CloudCourse.objects.all().order_by("ID")
    if (strVar == 'LessonCategory'): 
        res = LessonCategory.objects.all().order_by("Order")
    if (strVar == 'UserPointRate'): 
        res = UserPointRate.objects.all().order_by("ID")
    #if (strVar == 'wxObjTsaiReader'):
        #res = wxAccountInterface(wxAccounts.objects.filter(appId = "wx3a6ed5af1b0f81d6")[0])
 
    mc.set(strVar, res)
    return True

#def updateCache():
#    for key in mc: