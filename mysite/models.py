#coding: utf-8
from django.db import models  
import datetime

# Create your models here.  
  
class Articles(models.Model): 
    ID = models.IntegerField(primary_key=True)
    PostDate = models.DateField()
    Author = models.CharField(max_length=100)
    #openID = models.CharField(max_length=256)
    Content = models.TextField()
    ArticleURL = models.CharField(max_length=2048)
    Title = models.CharField(max_length=256)
    ArticleAbstract = models.TextField()
    Thumbnail = models.CharField(max_length=512)
    SourceAccount = models.CharField(max_length=128)
    MediaID = models.CharField(max_length=128)
    TitlePicture = models.CharField(max_length=1024)
    RewardCode = models.CharField(max_length=1024)
    #ArticleType = models.CharField(max_length=64,default='')
    #ParentID = models.IntegerField(default=0)
    class Meta:
        db_table  = 'wechatArticles'
        
class Schedule(models.Model):
    ID = models.IntegerField(primary_key=True)
    Author = models.CharField(max_length=512)
    openID = models.CharField(max_length=256)
    AuthorBio = models.CharField(max_length=512)
    ScheduleDate = models.DateField()
    PostDate = models.DateTimeField(default=datetime.datetime.now())
    ArticleURL = models.CharField(max_length=512)
    ArticleContent = models.TextField()
    Expired = models.IntegerField(default=0)
    Title = models.CharField(max_length=128)
    Editor = models.CharField(max_length=128)
    TitlePicture = models.CharField(max_length=1024)
    RewardCode = models.CharField(max_length=1024)
    ArticleType = models.CharField(max_length=64,default='')
    ParentID = models.IntegerField(default=0)
    ISTop = models.IntegerField(default=0)
    TopicID = models.IntegerField(default=0)
    ChatID = models.IntegerField(default=0) 
    class Meta:
        db_table  = 'Schedule'
        
class ScheduleBak(models.Model):
    ID = models.IntegerField(primary_key=True)
    Author = models.CharField(max_length=512)
    openID = models.CharField(max_length=256)
    AuthorBio = models.CharField(max_length=512)
    ScheduleDate = models.DateField()
    PostDate = models.DateTimeField(default=datetime.datetime.now())
    ArticleURL = models.CharField(max_length=512)
    ArticleContent = models.TextField()
    Expired = models.IntegerField(default=0)
    Title = models.CharField(max_length=128)
    Editor = models.CharField(max_length=128)
    TitlePicture = models.CharField(max_length=1024)
    RewardCode = models.CharField(max_length=1024)
    ArticleType = models.CharField(max_length=64,default='')
    ParentID = models.IntegerField(default=0)
    ISTop = models.IntegerField(default=0)
    TopicID = models.IntegerField(default=0)
    ChatID = models.IntegerField(default=0) 
    class Meta:
        db_table  = 'ScheduleBak'  
        
class PageLog(models.Model):
    ID = models.IntegerField()
    URL = models.CharField(max_length=512)
    IPAddress = models.CharField(max_length=128)
    LogInfo = models.TextField()
    TimeStamp = models.DateTimeField()
    Invoker = models.CharField(max_length=256)
    LogType = models.CharField(max_length=128)
    class Meta:
        db_table  = 'Log'   
        
        
class wxAccounts(models.Model):
    appId = models.CharField(max_length=128)
    appName = models.CharField(max_length=256)
    Alias = models.CharField(max_length=128)
    ProcessIndex = models.IntegerField(default=0)
    UserCount = models.IntegerField(default=0)
    headImg = models.CharField(max_length=512)
    serviceTypeInfo = models.IntegerField()
    appUsername = models.CharField(max_length=128)
    QRCodeURL = models.CharField(max_length=512)
    AuthCode = models.CharField(max_length=256) #access_token
    Expired = models.DateTimeField()
    RefreshCode = models.CharField(max_length=128)
    OnboardDate = models.DateTimeField(default=datetime.datetime.now())
    Disabled = models.IntegerField(default=0)
    AutoReply = models.CharField(max_length=512)
    Config = models.CharField(max_length=1024)
    NextOpenID = models.CharField(default = 'StartOpenID')
    class Meta:
        db_table = "wxAccounts"
        
class wxConfig(models.Model):
    appid = models.CharField(max_length=128)
    ConfigName = models.CharField(max_length=128)
    ConfigValue = models.CharField(max_length=128)
    class Meta:
        db_table = "wxConfig"
        
class OITM(models.Model):
    ID = models.AutoField(primary_key=True)
    ProductID = models.IntegerField(default=0) #MiniProductID
    ProductName = models.CharField(max_length=128)
    ProductCode = models.CharField(max_length=64)
    ProductType = models.CharField(max_length=64)
    AppID = models.CharField(max_length=256)
    OwnerOpenId = models.CharField(max_length=256)
    PaidOpenId = models.CharField(max_length=256)
    Size = 	models.CharField(max_length=128)
    Color = models.CharField(max_length=128)
    Quantity = 	models.IntegerField(default=0)
    TotalAmount = models.IntegerField(default=0)
    Paid = models.IntegerField(default=0)
    wxPayURL = 	models.CharField(max_length=512)
    BBSID = models.CharField(max_length=16)
    Name = models.CharField(max_length=128)
    Tel = models.CharField(max_length=128)
    Address = models.CharField(max_length=512)
    PrePay_ID = models.CharField(max_length=128)
    TransactionID = models.CharField(max_length=128)
    TradeNumber = models.CharField(max_length=128)
    TradeTime = models.DateTimeField(default=datetime.datetime.now())
    SKU = models.CharField(max_length=256)
    Messages = models.CharField(max_length=512)
    Mobile = models.CharField(max_length=64)
    ChannelID = models.IntegerField(default=0)
    DistributorID = models.IntegerField(default=0) #wxUser.ID
    PaidPoints = models.IntegerField(default=0)
    class Meta:
        db_table = "OITM"    
    
class UserPointDetail(models.Model):
    ID = models.AutoField(primary_key=True)
    UserID = models.IntegerField(default=0)
    wxUserID = models.IntegerField(default=0)
    Points = models.IntegerField(default=0)
    SpentPoints = models.IntegerField(default=0)
    ObjectType = models.CharField(max_length=64)
    ObjectID = models.IntegerField(default=0)
    Reason = models.CharField(max_length=256)
    IsHandled = models.IntegerField(max_length=4,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "UserPointDetail"
        
class UserCashbackDetail(models.Model):
    ID = models.AutoField(primary_key=True)
    UserID = models.IntegerField(default=0)
    wxUserID = models.IntegerField(default=0)
    Amount = models.IntegerField(default=0)
    SpentAmount = models.IntegerField(default=0)
    ObjectType = models.CharField(max_length=64)
    ObjectID = models.IntegerField(default=0)
    Reason = models.CharField(max_length=256)
    IsHandled = models.IntegerField(max_length=4,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "UserCashbackDetail"  
        
class UserPointRate(models.Model):
    ID = models.AutoField(primary_key=True)
    Code = models.CharField(max_length=64)
    Name = models.CharField(max_length=64)
    Rate = models.DecimalField(max_digits=11,decimal_places=2, default=0.00)
    class Meta:
        db_table = "UserPointRate"     
    
class DefaultConfig(models.Model):
    ConfigName = models.CharField(max_length=128)
    ConfigValue = models.CharField(max_length=128)
    ConfigType = models.CharField(max_length=128)
    CName = models.CharField(max_length=128)
    Enable = models.IntegerField(default=1)
    ConfigOrder = models.IntegerField(default=100)
    class Meta:
        db_table = "DefaultConfig"     
    
    
class Sheet1(models.Model):
    Owner = models.CharField(max_length=128)
    ID = models.IntegerField(default = 0)
    Title = models.CharField(max_length=256)
    EnTitle = models.CharField(max_length=256)
    City = models.CharField(max_length=128)
    website = models.CharField(max_length=512)
    InternalID = models.IntegerField(default = 0)
    CreateTime = models.DateTimeField(default=datetime.datetime.now())
    LastModified = models.CharField(max_length=256)
    PageSize = models.IntegerField(default = 0)
    class Meta:
        db_table = "Sheet1"     

class Comment(models.Model):
    ID = models.IntegerField()
    ArticleID = models.IntegerField()
    content = models.TextField()
    UserName = models.CharField(max_length=128)
    PostDate= models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "Comment"     

        

class wxUser(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=128)
    Avatar = models.CharField(max_length=512)
    Gender = models.CharField(max_length=8)
    Role = models.CharField(max_length=128) 
    JoinTime = models.DateTimeField(default=datetime.datetime.now())
    unionID = models.CharField(max_length=256)
    Country = models.CharField(max_length=128) 
    City =  models.CharField(max_length=128) 
    Province =  models.CharField(max_length=128) 
    openID = models.CharField(max_length=256)
    PublicAppID = models.CharField(default = '')
    SourceAccount = models.CharField(max_length=128)
    Subscribed = models.IntegerField(default=0)
    Birthday = models.DateTimeField(default=None)
    Company = models.CharField(max_length=256)
    Industry = models.CharField(max_length=256)
    Salary = models.CharField(max_length=128)
    Province2 = models.CharField(max_length=64)
    City2 = models.CharField(max_length=64)
    DateOfFirstJob = models.DateTimeField(default=None)
    University = models.CharField(max_length=256)
    Major = models.CharField(max_length=256)
    Growth = models.IntegerField(default=0)
    UserCode = models.CharField(max_length=128)
    Mobile = models.CharField(max_length=64)
    VerificationCode = models.IntegerField()
    VerificationCodeExpired = models.DateTimeField(default=datetime.datetime.now())
    MobileBound  = models.BooleanField(default=False)  #绑定
    QRCodeTicket = models.CharField(max_length=64,default=None)
    Updated = models.DateTimeField(default=datetime.datetime.now())
    DailySendTimes = models.IntegerField(default=0)
    Points = models.IntegerField(default=0)
    class Meta:
        db_table = "wxUser"   

class wxProduct(models.Model):
    ID = models.IntegerField(primary_key=True)
    appid = models.CharField(max_length=128)
    ProductCode =  models.CharField(max_length=128)
    ProductType =  models.CharField(max_length=128)
    ProductName =  models.CharField(max_length=128)
    price = models.IntegerField(max_length=64)
    mchid = models.CharField(max_length=128)
    notifyUrl = models.CharField(max_length=1024)
    class Meta:
        db_table = "wxProduct"
        
        
        
class Role(models.Model):
    ID = models.IntegerField(primary_key=True)
    RoleName = models.CharField(max_length=64)
    Description = models.CharField(max_length=256)
    Authorities = models.CharField(max_length=256)
    class Meta:
        db_table = "Role"
        
class PaidArticles(models.Model):
    ID = models.IntegerField(primary_key=True)
    ArticleID = models.CharField(max_length=64)
    ArticleName = models.CharField(max_length=256)
    ArticleUrl = models.CharField(max_length=256)
    PayUrl = models.CharField(max_length=256)
    AuthorName = models.CharField(max_length=64)
    OwnerOpenID = models.CharField(max_length=256)
    CreateTime = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "PaidArticles"

class Product(models.Model):
    ID = models.AutoField(primary_key=True)
    ProductCode = models.CharField(max_length=64)
    ProductTypeID = models.IntegerField(max_length=11,default=0)
    LessonCategoryID = models.IntegerField(max_length=11,default=0)
    ProductName = models.CharField(max_length=256)
    ProductUrl1 = models.CharField(max_length=256,default='')
    ProductUrl2 = models.CharField(max_length=256,default='')
    ProductUrl3 = models.CharField(max_length=256,default='')
    ProductUrl4 = models.CharField(max_length=256,default='')
    ProductUrl5 = models.CharField(max_length=256,default='')
    ProductUrl6 = models.CharField(max_length=256,default='')
    ProductUrl7 = models.CharField(max_length=256,default='')
    ProductUrl8 = models.CharField(max_length=256,default='')
    ProductUrl9 = models.CharField(max_length=256,default='')
    ProductUrl10 = models.CharField(max_length=256,default='')
    ProductUrl11 = models.CharField(max_length=256,default='')
    ShareDescription = models.CharField(max_length=1024)
    Groups = models.CharField(max_length=64)
    HotPoint = models.CharField(max_length=256)
    SKUName = models.CharField(max_length=256)
    Price = models.IntegerField(max_length=11,default=0)
    OriginalPrice = models.IntegerField(max_length=11,default=0)
    Inventory = models.IntegerField(max_length=11,default=0)
    CostPrice = models.IntegerField(max_length=11,default=0)
    Messages = models.CharField(max_length=512)
    #IsDisplay = models.IntegerField(max_length=4,default=0)
    #AutoListingTime = models.DateTimeField(default=None)
    PutawayChannels = models.CharField(max_length=256)
    ProductProperties = models.CharField(max_length=256)
    TeacherDesc = models.CharField(max_length=256)
    Order = models.IntegerField(default =0)
    SetSKU = models.IntegerField(max_length=4,default =0)
    DistributePoint = models.IntegerField(default =0)
    DistributeCashback = models.IntegerField(default =0)
    PointLimit = models.IntegerField(default =0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "Product"
        

class ProductType(models.Model):
    ID = models.AutoField(primary_key=True)
    Code = models.CharField(max_length=64)
    Name = models.CharField(max_length=64)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "ProductType"
        
        
class ProductMessageType(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=64)
    RegularExpression = models.CharField(max_length=128)
    InputType = models.CharField(max_length=64)
    Placeholder = models.CharField(max_length=64)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "ProductMessageType"
        
        
class ProductMessage(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=64)
    ProductMessageTypeID = models.IntegerField(max_length=11,default=0)
    ProductID = models.IntegerField(max_length=11,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "ProductMessage"
        
        
class UserBuyMessages(models.Model):
    ID = models.AutoField(primary_key=True)
    UserID = models.IntegerField(max_length=11,default=0)
    wxUserID = models.IntegerField(max_length=11,default=0)
    Name = models.CharField(max_length=128)
    wxCode = models.CharField(max_length=128)
    Age = models.IntegerField(max_length=11,default=0)
    Grade = models.IntegerField(max_length=11,default=0)
    IsDefault = models.IntegerField(max_length=4,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "UserBuyMessages"
        
        
class ProductTag(models.Model):
    ID = models.AutoField(primary_key=True)
    Code = models.CharField(max_length=64)
    Name = models.CharField(max_length=64)
    FullName = models.CharField(max_length=256)
    ShowCount = models.IntegerField(max_length=11,default=0)
    TitleImg = models.CharField(max_length=256)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "ProductTag"
        
        
class ProductAndProductTag(models.Model):
    ID = models.AutoField(primary_key=True)
    ProductID = models.IntegerField(max_length=11,default=0)
    ProductTagID = models.IntegerField(max_length=11,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "ProductAndProductTag"
        
        
class MiniappProduct(models.Model):
    ID = models.AutoField(primary_key=True)
    Code = models.CharField(max_length=64)
    Name = models.CharField(max_length=256)
    ProductTypeID = models.IntegerField(max_length=11,default=0)
    LessonCategoryID = models.IntegerField(max_length=11,default=0)
    ProductID = models.IntegerField(max_length=11,default=0)
    ProductUrl1 = models.CharField(max_length=256,default='')
    ProductUrl2 = models.CharField(max_length=256,default='')
    ProductUrl3 = models.CharField(max_length=256,default='')
    ProductUrl4 = models.CharField(max_length=256,default='')
    ProductUrl5 = models.CharField(max_length=256,default='')
    ProductUrl6 = models.CharField(max_length=256,default='')
    ProductUrl7 = models.CharField(max_length=256,default='')
    ProductUrl8 = models.CharField(max_length=256,default='')
    ProductUrl9 = models.CharField(max_length=256,default='')
    ProductUrl10 = models.CharField(max_length=256,default='')
    ProductUrl11 = models.CharField(max_length=256,default='')
    #ShareDescription = models.CharField(max_length=1024)
    #Groups = models.CharField(max_length=64)
    #HotPoint = models.CharField(max_length=256)
    SKUName = models.CharField(max_length=256)
    Price = models.IntegerField(max_length=11,default=0)
    OriginalPrice = models.IntegerField(max_length=11,default=0)
    Inventory = models.IntegerField(max_length=11,default=0)
    CostPrice = models.IntegerField(max_length=11,default=0)
    Messages = models.CharField(max_length=512)
    IsDisplay = models.IntegerField(max_length=4,default=0)
    ProductProperties = models.CharField(max_length=256)
    TeacherDesc = models.CharField(max_length=256)
    Order = models.IntegerField(default =0)
    DistributePoint = models.IntegerField(default =0)
    DistributeCashback = models.IntegerField(default =0)
    PointLimit = models.IntegerField(default =0)
    #AutoListingTime = models.DateTimeField(default=None)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "MiniappProduct"
        
        
class MiniappTeacher(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=256)
    TeacherUrl1 = models.CharField(max_length=256)
    TeacherUrl2 = models.CharField(max_length=256)
    TeacherUrl3 = models.CharField(max_length=256)
    TeacherUrl4 = models.CharField(max_length=256)
    TeacherUrl5 = models.CharField(max_length=256)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "MiniappTeachers"
        
        
class MiniappBanner(models.Model):
    ID = models.AutoField(primary_key=True)
    URL = models.CharField(max_length=256)
    Order = models.IntegerField(default =0)
    LessonCategoryID = models.IntegerField(max_length=11,default=0)
    LinkProductID = models.IntegerField(max_length=11,default=0)#MiniappProductID
    ShowOnMainpage = models.IntegerField(max_length=4,default=1)
    class Meta:
        db_table = "MiniappBanners"
        
        
class MiniappCampaignBanner(models.Model):
    ID = models.AutoField(primary_key=True)
    URL = models.CharField(max_length=256)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "CampaignBanner"
        
        
class MiniappCashbackBanner(models.Model):
    ID = models.AutoField(primary_key=True)
    URL = models.CharField(max_length=256)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "CashbackBanner"        
        
        
class MiniappCampaignTags(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=64)
    ChildName = models.CharField(max_length=64)
    IsSpecial = models.IntegerField(max_length=4,default=0)
    Order = models.IntegerField(max_length=11,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "CampaignTags"
        
        
class MiniappCampaignTagProduct(models.Model):
    ID = models.AutoField(primary_key=True)
    CampaignTagID = models.IntegerField(max_length=11,default=0) #MiniappCampaignTagID
    MiniProductID = models.IntegerField(max_length=11,default=0)
    TitleImg = models.CharField(max_length=256)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "CampaignTagProduct"
        
        
class FormID(models.Model):
    ID = models.IntegerField(primary_key=True)
    OpenID = models.CharField(max_length=256)
    FID = models.CharField(max_length=256)
    NickName = models.CharField(max_length=256)
    LastCount = models.IntegerField(default =0)
    PostTime = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "FormID" 
        
        
class BusinessSpending(models.Model):
    ID = models.IntegerField(primary_key=True)
    TradeNo = models.CharField(max_length=64)
    Amount = models.IntegerField(default=0)
    ProductCode = models.CharField(max_length=64)
    ProductType = models.CharField(max_length=64)
    TargetOpenID = models.CharField(max_length=256)
    PayedTime = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "BusinessSpending"
        
        
class Authority(models.Model):
    ID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=64)
    Description = models.CharField(max_length=256)
    Type = models.IntegerField(default =1)
    class Meta:
        db_table = "Authority"  
        
        
class AuthorityType(models.Model):
    ID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=64)
    Description = models.CharField(max_length=256)
    class Meta:
        db_table = "AuthorityType"  
    
            
class Channel(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=256)
    Remark = models.CharField(max_length=512)
    Editable = models.IntegerField(default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "Channels"
        
        
class User(models.Model):
    ID = models.AutoField(primary_key=True)
    IsImported = models.BooleanField(default=False)  #是否已经导入过
    Name = models.CharField(max_length=256)
    ChannelID = models.IntegerField(default=0)
    Province = models.CharField(max_length=64)
    City = models.CharField(max_length=64)
    District = models.CharField(max_length=64)
    Zip = models.CharField(max_length=64)
    Address = models.CharField(max_length=256)
    Mobile = models.CharField(max_length=64)
    Email = models.CharField(max_length=128)
    WechatCode = models.CharField(max_length=64)
    OpenID = models.CharField(max_length=128)
    Created = models.DateTimeField(default=datetime.datetime.now())
    TimeStamp = models.DateTimeField(default=datetime.datetime.now())
    DistributorName = models.CharField(max_length=128) #分销商名称
    TagIDs = models.CharField(max_length=512)
    SegmentName = models.CharField(max_length=64)
    ChildAge = models.IntegerField(default=0)
    ChildGrade = models.IntegerField(default=0)
    ChildName = models.CharField(max_length=64,default=None)
    Campaign = models.CharField(max_length=64)
    NickName = models.CharField(max_length=64)
    LastLoginTime = models.DateTimeField(default=None)
    EdusohoID = models.IntegerField(max_length=11,default=None)
    Role = models.IntegerField(max_length=4,default=0) #0为普通学员，1为教师，不在用户列表显示
    class Meta:
        db_table = "Users"
        
class TradeInfo(models.Model):
    ID = models.IntegerField(primary_key=True)
    IsImported = models.BooleanField(default=False)  #是否已经导入过
    UserID = models.IntegerField(default=0)       #用户ID
    TradeID = models.CharField(max_length=128)    #交易ID,订单号
    ChannelID = models.IntegerField(default=0)    #来源ID
    OrderCount = models.IntegerField(default=0)   #订单数量（有赞可能会有一个交易多个订单）
    Name = models.CharField(max_length=256)       #订单名，课程名
    TradeType = models.CharField(max_length=128)  #交易类型 有赞 取值范围：<br> FIXED （一口价）<br> GIFT （送礼）<br> BULK_PURCHASE（来自分销商的采购）<br> PRESENT （赠品领取）<br> GROUP （拼团订单）<br> PIFA （批发订单）<br> COD （货到付款）<br> PEER （代付）<br> QRCODE（扫码商家二维码直接支付的交易）<br> QRCODE_3RD（线下收银台二维码交易)
    BuyerMessage = models.CharField(max_length=512) #买家留言
    TradeMessage = models.CharField(max_length=512) #卖家备注
    FeedBack = models.IntegerField(default=0)       #交易维权状态。<br> 0 无维权，1 顾客发起维权，2 顾客拒绝商家的处理结果，3 顾客接受商家的处理结果，9 商家正在处理,101 维权处理中,110 维权结束。<br> 备注：1到10的状态码是微信维权状态码，100以上的状态码是有赞维权状态码
    OuterTradeID = models.CharField(max_length=128) #外部交易编号
    TransactionID = models.CharField(max_length=128) #支付流水号
    Status = models.CharField(max_length=64)         #交易状态。有赞 取值范围： TRADE_NO_CREATE_PAY (没有创建支付交易) WAIT_BUYER_PAY (等待买家付款) WAIT_PAY_RETURN (等待支付确认) WAIT_GROUP（等待成团，即：买家已付款，等待成团） WAIT_SELLER_SEND_GOODS (等待卖家发货，即：买家已付款) WAIT_BUYER_CONFIRM_GOODS (等待买家确认收货，即：卖家已发货) TRADE_BUYER_SIGNED (买家已签收) TRADE_CLOSED (付款以后用户退款成功，交易自动关) TRADE_INVALID （订单无效，当前状态无需处理）
    TotalFee = models.DecimalField(max_digits=12,decimal_places=2, default=0.00)  #总额
    PostFee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  #邮费
    RefundedFee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  #退款金额
    DiscountFee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  #折扣价格
    Payment = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  #实付金额
    Created = models.DateTimeField(default=datetime.datetime.now())  #创建时间
    Updated = models.DateTimeField(default=datetime.datetime.now())  #更新时间
    PayTime = models.DateTimeField(default=datetime.datetime.now())  #支付时间
    PayType = models.CharField(max_length=64)                       #支付类型 有赞 取值范围： WEIXIN (微信自有支付) WEIXIN_DAIXIAO (微信代销支付) ALIPAY (支付宝支付) BANKCARDPAY (银行卡支付) PEERPAY (代付) CODPAY (货到付款) BAIDUPAY (百度钱包支付) PRESENTTAKE (直接领取赠品) COUPONPAY(优惠券/码全额抵扣) BULKPURCHASE(来自分销商的采购) MERGEDPAY(合并付货款) ECARD(有赞E卡支付) PURCHASE_PAY (采购单支付)
    TuanNo = models.CharField(max_length=128)                      #拼团编号
    IsTuanHead = models.IntegerField(default=0)                   #是否团长
    OrderID = models.IntegerField(default=0)                  #订单ID,有赞特有，一个交易下可能有多个订单
    ProdID = models.IntegerField(default=0)                  #产品，课程ID
    SKUID = models.IntegerField(default=0)               #skuID 和ProdID一起才能唯一确定产品 有赞特有
    SKUCode = models.CharField(max_length=128)           #SKU编码
    SKUName = models.CharField(max_length=256)           #SKU名称
    ProdCount = models.IntegerField(default=0)           #产品数，可能会买多个
    OuterSKUID = models.CharField(max_length=128)        #外部SKUID
    OuterProdID = models.CharField(max_length=128)       #外部ProdID
    ThirdPartyID = models.IntegerField(default=None)       #第三方课程ID
    DistributorName = models.CharField(max_length=128)       #分销商名称
    DistributorID = models.IntegerField(default=None)      #分销商ID
    DistributorType = models.CharField(max_length=64)       #分销商类型
    Relations = models.CharField(max_length=1024)       #相关订单
    TimeStamp = models.DateTimeField(default=datetime.datetime.now())
    IsNewUserTrade = models.BooleanField(default=False)  #是否新用户订单
    LessonCategoryID = models.IntegerField(default=None) #课程分类
    IsRefund = models.IntegerField(max_length=4,default=0)
    IsLessonTemplateNotified = models.IntegerField(max_length=4,default=0)
    class Meta:
        db_table = "TradeInfo"  
        
class Coupons(models.Model):
    ID = models.AutoField(primary_key=True)
    CouponID = models.IntegerField(max_length=11)
    KDTID = models.IntegerField(max_length=11)
    GroupType = models.IntegerField(max_length=11)
    Name = models.CharField(max_length=256)
    PreferentialType = models.IntegerField(max_length=11)
    Denominations = models.IntegerField(max_length=11)
    ValueRandomTo = models.IntegerField(max_length=11,default=0)
    Condition = models.IntegerField(max_length=11,default=0)
    Discount = models.IntegerField(max_length=11)
    IsLimit = models.IntegerField(max_length=11)
    IsForbidPreference = models.IntegerField(max_length=11)
    UserLevel = models.IntegerField(max_length=11)
    DateType = models.IntegerField(max_length=11)
    FixedTerm = models.IntegerField(max_length=11)
    FixedBeginTerm = models.IntegerField(max_length=11)
    ValidStartTime = models.DateTimeField(default=None)
    ValidEndTime = models.DateTimeField(default=None)
    TotalQTY = models.IntegerField(max_length=11)
    StockQTY = models.IntegerField(max_length=11)
    RangeType = models.CharField(max_length=64)
    RangeValue = models.CharField(max_length=4096)
    ExpireNotice = models.CharField(max_length=64)
    Description = models.CharField(max_length=1024)
    IsShare = models.IntegerField(max_length=11)
    IsInvalid = models.IntegerField(max_length=11)
    TotalTake = models.IntegerField(max_length=11)
    TotalUsed = models.IntegerField(max_length=11)
    Created = models.DateTimeField(default=None)
    Updated = models.DateTimeField(default=None)
    TimeStamp = models.DateTimeField(default=datetime.datetime.now())
    URL = models.CharField(max_length=512)
    class Meta:
        db_table = "Coupons"

        
class UserCoupons(models.Model):
    ID = models.AutoField(primary_key=True)
    UserID = models.IntegerField(max_length=11,default=0)
    Mobile = models.CharField(max_length=64)
    Name = models.CharField(max_length=64)
    CouponName = models.CharField(max_length=256)
    Fee = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    ExpireAt = models.DateTimeField(default=datetime.datetime.now())
    TakeAt = models.DateTimeField(default=datetime.datetime.now())
    IsValid = models.IntegerField(max_length=4,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    CouponID = models.IntegerField(max_length=11,default=0)
    CouponGroupID = models.IntegerField(max_length=11,default=0)
    class Meta:
        db_table = "UserCoupons"
        
    
class LessonTemplate(models.Model):
    ID = models.IntegerField(primary_key=True)
    YouzanName = models.CharField(max_length=256)
    YouzanSKU = models.CharField(max_length=256)
    DazhiName = models.CharField(max_length=256)
    DazhiCode = models.CharField(max_length=64)
    TeachingPlan = models.CharField(max_length=128)
    XiaoeName = models.CharField(max_length=256)
    class Meta:
        db_table = "dzLessonTemplate"
        
        
class Lesson(models.Model):
    ID = models.IntegerField(primary_key=True)
    Code = models.CharField(max_length=64)
    Name = models.CharField(max_length=256)
    TeachingPlan = models.CharField(max_length=128)
    Status = models.IntegerField(default=0) 
    class Meta:
        db_table = "Lessons"
        
        
class LessonsOfThirdParty(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=256)
    SKUName = models.CharField(max_length=256)
    ChannelID = models.IntegerField(default=0)
    TelMsgTemplateID = models.IntegerField(default=1)
    wxMsgTemplateIDs = models.CharField(max_length=64)
    LessonCategoryID = models.IntegerField(default=0)
    ProductID = models.IntegerField(default=0)
    class Meta:
        db_table = "LessonsOfThirdParty"
        
        
class LessonCategory(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=64)
    Code = models.CharField(max_length=64)
    FullName = models.CharField(max_length=256)
    Icon = models.CharField(max_length=256)
    TitleImg = models.CharField(max_length=256)
    Order = models.IntegerField(default=0)
    ShowTag = models.IntegerField(default=0,max_length=4)
    ShowCount = models.IntegerField(max_length=11,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "LessonCategory"
        
        
class LessonsRelation(models.Model):
    ID = models.IntegerField(primary_key=True)
    LessonID = models.IntegerField(default=0) 
    ThirdPartyID = models.IntegerField(default=0) 
    class Meta:
        db_table = "LessonsRelation"
        
class ImportInfo(models.Model):
    ID = models.IntegerField(primary_key=True)
    Info = models.TextField()
    TimeStamp = models.DateTimeField(default=datetime.datetime.now())
    InfoType = models.CharField(max_length=128) 
    class Meta:
        db_table = "ImportInfo"
        
class ImportDetail(models.Model):
    ID = models.IntegerField(primary_key=True)
    TradeID = models.CharField(max_length=128)
    ChannelID = models.IntegerField(default=0) 
    IsSucceeded = models.BooleanField(default=False)  #是否导入成功
    FailedType = models.CharField(max_length=128)
    Info = models.CharField(max_length=512)
    LessonName = models.CharField(max_length=256)
    Mobile = models.CharField(max_length=64)
    TimeStamp = models.DateTimeField(default=datetime.datetime.now())
    MsgSentInfo = models.CharField(max_length=256)  #短信是否发送成功
    class Meta:
        db_table = "ImportDetails"
        
class TelMsgTemplate(models.Model):
    ID = models.IntegerField(primary_key=True)
    MsgID = models.IntegerField(default=0) 
    Content = models.CharField(max_length=1024)
    class Meta:
        db_table = "TelMsgTemplate"
        
        
class wxMsgTemplate(models.Model):
    ID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=256)
    TemplateID = models.CharField(max_length=128)
    KeywordCount = models.IntegerField(default=0) 
    RedirectUrl = models.CharField(max_length=256)
    First = models.CharField(max_length=256)
    Remark = models.CharField(max_length=256)
    Keyword1 = models.CharField(max_length=256)
    Keyword2 = models.CharField(max_length=256)
    Keyword3 = models.CharField(max_length=256)
    Keyword4 = models.CharField(max_length=256)
    Keyword5 = models.CharField(max_length=256)
    Keyword6 = models.CharField(max_length=256)
    class Meta:
        db_table = "wxMsgTemplate"
        

class UserTag(models.Model):
    ID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=128)
    TagType = models.CharField(max_length=64)
    Description = models.CharField(max_length=512)
    Rules = models.CharField(max_length=1024)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    UnionID = models.CharField(max_length=64)
    NickName = models.CharField(max_length=64)
    class Meta:
        db_table = "UserTag"
        
class MessageLog(models.Model):
    ID = models.IntegerField(primary_key=True)
    MsgType = models.CharField(max_length=64)
    OpenID = models.CharField(max_length=128)
    Mobile = models.CharField(max_length=64)
    Content = models.CharField(max_length=1024)
    Result = models.CharField(max_length=256)
    Created = models.DateTimeField(default=datetime.datetime.now())
    MsgInfoID = models.IntegerField(max_length=11)
    IsRead = models.IntegerField(max_length=4,default=0)
    class Meta:
        db_table = "MessageLog"
        
        
class MessageInfo(models.Model):
    ID = models.AutoField(primary_key=True)
    MsgType = models.CharField(max_length=64)
    Content = models.CharField(max_length=1024)
    Targets = models.TextField(default=None)
    MsgCount = models.IntegerField(max_length=11)
    ReceivedCount = models.IntegerField(max_length=11,default=0)
    ReadCount = models.IntegerField(max_length=11,default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    token = models.IntegerField(max_length=11,default=0)
    rd_url = models.CharField(max_length=256)
    class Meta:
        db_table = "MessageInfo"
        
        
class Campaign(models.Model):
    ID = models.IntegerField(primary_key=True)
    Code = models.CharField(max_length=64)
    CName = models.CharField(max_length=256)
    Balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    StartDate = models.DateField(default=None)
    EndDate = models.DateField(default=None)
    Remark = models.CharField(max_length=256,default=None)
    URL = models.CharField(max_length=128)
    class Meta:
        db_table = "Campaign"
        
        
class UserCampaign(models.Model):
    ID = models.AutoField(primary_key=True)
    UserID = models.IntegerField(max_length=11)
    CampaignID = models.IntegerField(max_length=11)
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "UserCampaign"
        
        
class question_answer(models.Model):
    ID = models.AutoField(primary_key=True)
    Question = models.CharField(max_length=150)
    Answer = models.TextField()
    Created = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "question_answer"

        
class CloudCourse(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=64, default=None)
    SKUName1 = models.CharField(max_length=64, default=None)
    SKUValue1 = models.CharField(max_length=64, default=None)
    SKUName2 = models.CharField(max_length=64, default=None)
    SKUValue2 = models.CharField(max_length=64, default=None)
    SKUName3 = models.CharField(max_length=64, default=None)
    SKUValue3 = models.CharField(max_length=64, default=None)
    SKUName4 = models.CharField(max_length=64, default=None)
    SKUValue4 = models.CharField(max_length=64, default=None)
    Scheduled = models.IntegerField(max_length=4, default=0)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "CloudCourse"
        
        
class CloudCourseLesson(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=64, default=None)
    CloudCourseID = models.IntegerField(max_length=11)
    IsFinished = models.IntegerField(max_length=4, default=0)
    StartTime = models.DateTimeField(default=datetime.datetime.now())
    EndTime = models.DateTimeField(default=datetime.datetime.now())
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "CloudCourseLesson"
        
        
class CloudCourseMember(models.Model):
    ID = models.AutoField(primary_key=True)
    UserID = models.IntegerField(max_length=11)
    Mobile = models.CharField(max_length=64, default=None)
    Name = models.CharField(max_length=64, default=None)
    CloudCourseID = models.IntegerField(max_length=11)
    IsHide = models.IntegerField(max_length=4, default=0)
    CloudClassID = models.IntegerField(max_length=11, default=None)
    #CloudClassRoomID = models.IntegerField(max_length=11, default=None)
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    Role = models.IntegerField(max_length=4, default=0) #0普通学员，1老师
    class Meta:
        db_table = "CloudCourseMember"
        
        
class CloudClass(models.Model):
    ID = models.AutoField(primary_key=True)
    CloudCourseID = models.IntegerField(max_length=11)
    Name = models.CharField(max_length=64)
    PatrolInfo = models.CharField(max_length=256, default='')
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        db_table = "CloudClass"
        
        
class CloudClassRoom(models.Model):
    ID = models.AutoField(primary_key=True)
    CloudCourseID = models.IntegerField(max_length=11)
    CloudClassID = models.IntegerField(max_length=11)
    CloudCourseLessonID  = models.IntegerField(max_length=11, default=0)
    Name = models.CharField(max_length=64)
    Serial = models.IntegerField(max_length=11)
    Version = models.IntegerField(max_length=11)
    StartTime = models.DateTimeField(default=datetime.datetime.now())
    EndTime = models.DateTimeField(default=datetime.datetime.now())
    Created = models.DateTimeField(default=datetime.datetime.now())
    Updated = models.DateTimeField(default=datetime.datetime.now())
    TeacherPwd = models.CharField(max_length=64, default=None)
    PatrolPwd = models.CharField(max_length=64, default=None)
    AssistantPwd = models.CharField(max_length=64, default=None)
    StudentPwd = models.CharField(max_length=64, default=None)
    RoomType = models.IntegerField(max_length=4, default=3) #0：1v1 3：1v多
    VideoType = models.IntegerField(max_length=4, default=1) #0：176x144   1：320x240 2：640x480   3：1280x720 4：1920x1080
    VideoFramerate = models.IntegerField(max_length=4, default=10) #10,15,20,25,30
    ClassStart = models.IntegerField(max_length=4, default=0) #上课状态，0:未开始，1:上课中，2:已结束
    class Meta:
        db_table = "CloudClassRoom"
        
        
class dzhidianTest(models.Model):
    id = models.IntegerField(primary_key=True)
    verifiedMobile = models.IntegerField() 
    nickname = models.CharField(max_length=64)
    class Meta:
        db_table = "user"
        
class YouzanTrade(models.Model):
    ID = models.IntegerField(primary_key=True)
    #OldName = models.CharField(max_length=256)
    #NewName = models.CharField(max_length=256)
    YouzanName = models.CharField(max_length=256)
    class Meta:
        db_table = "YouzanTrade"
        
class Temp(models.Model):
    ID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=256)
    SKUName = models.CharField(max_length=256)
    class Meta:
        db_table = "temp"
        
class Cate1(models.Model):
    ID = models.IntegerField(primary_key=True)
    Category = models.CharField(max_length=256)
    YouzanName = models.CharField(max_length=256)
    LessonName = models.CharField(max_length=256)
    XiaoeName = models.CharField(max_length=256)
    class Meta:
        db_table = "cate1"
        
class Cate2(models.Model):
    ID = models.IntegerField(primary_key=True)
    Category = models.CharField(max_length=256)
    YouzanName = models.CharField(max_length=256)
    class Meta:
        db_table = "cate2"
        
class Cate3(models.Model):
    ID = models.IntegerField(primary_key=True)
    Category = models.CharField(max_length=64)
    DazhiName = models.CharField(max_length=128)
    class Meta:
        db_table = "cate3"
        
        