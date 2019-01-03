#-*- encoding:utf-8 -*-
from utils import *
from Crypto.Cipher import AES
from datetime import *
import time
import os
#import sys
import ssl
import urllib2
#import pymysql
import MySQLdb
import re
import threading
import io
import StringIO
#import ImageDraw
import point_views


CERTFILE = '../cert/apiclient_cert.pem'
KEYFILE = '../cert/apiclient_key.pem'
MINIAPPID = 'wxf11978168e04aba2'
#import datetime

class wxSign:
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        #print string
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret

class wxPaySign:
    def __init__(self, appid, prepay_id):
        self.ret = {
            'appId': appid,
            'nonceStr': self.__create_nonce_str(),
            'package': "prepay_id=%s"%prepay_id,
            'timeStamp': self.__create_timestamp(),
            'signType': 'MD5',
        }
        
    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        self.ret['signature'] = GetSign(self.ret)
        return self.ret
    
class wxCardSign:
    def __init__(self, jsapi_card_ticket, appid):
        self.ret = {
            'nonce_str': self.__create_nonce_str(),
            'api_ticket': jsapi_card_ticket,
            'time_stamp': self.__create_timestamp(),
            'app_id': appid

        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = ''.join(['%s' % (value) for value in sorted(self.ret.values())])
        
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret

def GetSign(values):
    m = hashlib.md5()
    retStr = ""
    items = values.items()
    items.sort()
    for key,value in items:
        Log("Item:%s"% items)
        retStr += "%s=%s&"%(key, value)
    Log("values:%s"% values)
    strParams = "%skey=IGWCHdS58OGbH4OkM1MIL9ZyV6QDQ1hp" % retStr 
    Log("GetSign for str: %s"%strParams)
    m.update(strParams)
    return m.hexdigest().upper()

def Decrypt(strEncrypt, msg_sign, timestamp, nonce):
    
    try:
        token = "TsaiWxHoutai"
        encodingAESKey = "dP6iTWijxbA0fTkLLJUurV6bBRvvGVaog9vrtBdJmbj"
        appid = "wx75d48dcb77431c72"
        #token = "2000000"
        #encodingAESKey = "jxWGeNqw7SPFNnMJuDeNbjaeWEXUh8cWmu8AosCoQZ4"
        #appid = "wxffa5d957de33a223"
        
        decrypt_test = WXBizMsgCrypt(token,encodingAESKey,appid)
        ret ,retStr = decrypt_test.DecryptMsg(strEncrypt, msg_sign, timestamp, nonce)
        if (ret==0):
            return retStr
        else:
            return ret
    except Exception, e:
        return e
def Encrypt(strToEncrypt, nonce, timestamp):
    try:
        token = "TsaiWxHoutai"
        encodingAESKey = "dP6iTWijxbA0fTkLLJUurV6bBRvvGVaog9vrtBdJmbj"
        appid = "wx75d48dcb77431c72"
        #token = "2000000"
        #encodingAESKey = "jxWGeNqw7SPFNnMJuDeNbjaeWEXUh8cWmu8AosCoQZ4"
        #appid = "wxffa5d957de33a223"
        
        decrypt_test = WXBizMsgCrypt(token,encodingAESKey,appid)
        ret ,retStr = decrypt_test.EncryptMsg(strToEncrypt, nonce, timestamp)
        if (ret==0):
            return retStr
        else:
            return ret
    except Exception, e:
        Log("Encrypt Error: %s"%e)
        return e

def TestWechatPay(request):
    try:
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
            ip =  request.META['HTTP_X_FORWARDED_FOR']  
        else:  
            if request.META.has_key('REMOTE_ADDR'):
                ip = request.META['REMOTE_ADDR']  
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        xml = """<xml>
	<appid>wx6c7fc6650e40fb00</appid>
	<attach>支付测试</attach>
	<body>微信支付测试</body>
	<mch_id>1236931302</mch_id>
	<nonce_str>1add1a30ac87aa2db72f57a2375d8abc</nonce_str>
	<notify_url>http://applinzi.ddianke.com/deny</notify_url>
	<out_trade_no>1415659999</out_trade_no>
	<product_id>1010110001898</product_id>
	<spbill_create_ip>167.220.232.147</spbill_create_ip>
	<total_fee>100</total_fee>
	<trade_type>NATIVE</trade_type>
	<sign>BF1393AF2B6FD33492362A0B2EA3941A</sign>
</xml>"""
        res = PostData(url, xml)
        Log(res)
    except Exception, e:
        Log("TestWechatPay Error: %s" % e)
    

    
def GetwxPrepayId(appid,price,quantity,product_id,productCode,productType,productName,openid,mchid,notifyUrl,goods_json=None,channel_id=0,distributor_id=0,paidpoints=0):
    try:
        nonce_str = int(time.time()*1000)
        out_trade_no = nonce_str
        total_fee = int(price) * int(quantity) - int(paidpoints*100)
        
        values = {
              "appid":appid,
              "attach":productCode,
              "body": productName,
              "device_info": "WEB",
              "fee_type": "CNY",
              "mch_id": mchid,
              "nonce_str":nonce_str,
              "notify_url":notifyUrl,
              "openid": openid,
              "out_trade_no":out_trade_no,
              "product_id": "1000989",
              "spbill_create_ip": "167.220.232.147",
              "total_fee": total_fee,
              "trade_type": "JSAPI",
              }
        sign =GetSign(values)
        Log(sign)
        
        xml = """<xml>
	<appid>%s</appid>
	<attach>%s</attach>
	<body>%s</body>
    <device_info>WEB</device_info>
    <fee_type>CNY</fee_type>
	<mch_id>%s</mch_id>
	<nonce_str>%s</nonce_str>
	<notify_url><![CDATA[%s]]></notify_url>
    <openid><![CDATA[%s]]></openid>
	<out_trade_no>%s</out_trade_no>
    <product_id>1000989</product_id>
	<spbill_create_ip><![CDATA[167.220.232.147]]></spbill_create_ip>
	<total_fee>%s</total_fee>
	<trade_type>JSAPI</trade_type>
	<sign><![CDATA[%s]]></sign>
</xml>"""%(appid, productCode, productName, mchid, nonce_str, notifyUrl, openid,out_trade_no, total_fee, sign)         
 
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        Log("Sign %s:"%xml,"local", "0.0.0.0", "DEBUG")

        res = PostData(url, xml.encode('UTF-8'))
        Log("GetwxPrepayId res:%s" % res,"local", "0.0.0.0", "DEBUG")
        xml = ET.fromstring(res)
        prepay_id = xml.find("prepay_id").text
        code_url = ''#xml.find("code_url").text
        mobile = ''
        user_name = ''
        #目前只有一个商品，需要添加用户配置信息，以便将来选择
        msgs = []
        sku = []
        if goods_json:
            sku = goods_json[0].get('skus',[])
            msgs = goods_json[0].get('messages',[])
            for msg in msgs:
                content = msg.split(':')
                if len(content) == 2 and content[0] == '手机号码':
                    mobile = content[1]
                if len(content) == 2 and content[0] == '学生姓名':
                    user_name = content[1]
        
        if mobile:
            wxuser = wxUserClass(appid,openid)
            wxuser.wxUserData.Mobile = mobile
            wxuser.wxUserData.save()
            user = User.objects.filter(Mobile=mobile)
            nickname = username = ''
            if wxuser.wxUserData.Name:
                nickname = username = wxuser.wxUserData.Name
            if user_name:
                username = user_name
            if not user:
                area = GetUserAreaByMobile(mobile)
                province = ''
                city = ''
                user_zip = ''
                segmentName = ''
                if type(area) is dict:
                    province = area.get('province', '')
                    city = area.get('cityName', '')
                    user_zip = area.get('postCode', '')
                    segmentName = area.get('segmentName', '')
                user = User(IsImported=False, Name=username, NickName=nickname, Mobile=mobile, ChannelID=channel_id, DistributorName=None, Province=province, 
                           City=city, Zip=user_zip, SegmentName=segmentName)
                user.save()
            else:
                user = user[0]
                if username:
                    user.Name = username
                if nickname:
                    user.NickName = nickname
                user.save()
        
        c = OITM(ProductID=product_id,ProductCode = productCode,ProductType = productType,ProductName = productName ,AppID=appid, PaidOpenId= openid , Quantity = quantity, TotalAmount = total_fee, 
                 TradeNumber = out_trade_no, wxPayURL =  code_url, PrePay_ID = prepay_id, SKU=';'.join(sku), Messages=json.dumps(msgs), Mobile=mobile,ChannelID=channel_id,
                 DistributorID=distributor_id, PaidPoints=paidpoints)#小程序的ChannelID
        c.save()
        #updateVar('OITM')
        return prepay_id
    except Exception, e:
        Log("GetwxPrepayId Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        return e
    
    
def GetPrepayId(appid,price,quantity,productCode,productName,openid,mchid,notifyUrl):
    try:
        nonce_str = int(time.time()*1000)
        out_trade_no = nonce_str
        total_fee = int(price) * int(quantity)
        
        values = {
              "appid":appid,
              "attach":productCode,
              "body": productName,
              "device_info": "WEB",
              "fee_type": "CNY",
              "mch_id": mchid,
              "nonce_str":nonce_str,
              "notify_url":notifyUrl,
              "openid": openid,
              "out_trade_no":out_trade_no,
              "product_id": "1000989",
              "spbill_create_ip": "167.220.232.147",
              "total_fee": total_fee,
              "trade_type": "JSAPI",
              }
        sign =GetSign(values)
        Log(sign)
        
        xml = """<xml>
	<appid>%s</appid>
	<attach>%s</attach>
	<body>%s</body>
    <device_info>WEB</device_info>
    <fee_type>CNY</fee_type>
	<mch_id>%s</mch_id>
	<nonce_str>%s</nonce_str>
	<notify_url><![CDATA[%s]]></notify_url>
    <openid><![CDATA[%s]]></openid>
	<out_trade_no>%s</out_trade_no>
    <product_id>1000989</product_id>
	<spbill_create_ip><![CDATA[167.220.232.147]]></spbill_create_ip>
	<total_fee>%s</total_fee>
	<trade_type>JSAPI</trade_type>
	<sign><![CDATA[%s]]></sign>
</xml>"""%(appid, productCode, productName, mchid, nonce_str, notifyUrl, openid,out_trade_no, total_fee, sign)         
 
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        Log("Sign %s:"%xml,"local", "0.0.0.0", "DEBUG")

        res = PostData(url, xml.encode('UTF-8'))
        Log("GetPrepayId res:%s" % res,"local", "0.0.0.0", "DEBUG")
        xml = ET.fromstring(res)
        prepay_id = xml.find("prepay_id").text
        return (prepay_id,out_trade_no)
    except Exception, e:
        Log("GetPrepayId Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        return (None,None)
    
    
def wxOrderRefund(appid,mchid,out_trade_no,transaction_id,total_fee,refund_fee,notify_url):
    try:
        nonce_str = int(time.time()*1000)
        refund_url ="https://api.mch.weixin.qq.com/secapi/pay/refund"
        values = {
              "appid":appid,
              "mch_id": mchid,
              "nonce_str":nonce_str,
              "notify_url":notify_url,
              "out_trade_no":out_trade_no,
              "out_refund_no":nonce_str,
              "total_fee": total_fee,
              "refund_fee": refund_fee
              }
        sign =GetSign(values)
        xml = """<xml>
   <appid>%s</appid>
   <mch_id>%s</mch_id>
   <nonce_str>%s</nonce_str> 
   <out_refund_no>%s</out_refund_no>
   <out_trade_no>%s</out_trade_no>
   <refund_fee>%d</refund_fee>
   <total_fee>%d</total_fee>
   <notify_url><![CDATA[%s]]></notify_url>
   <sign><![CDATA[%s]]></sign>
</xml>""" % (appid,mchid,nonce_str,nonce_str,out_trade_no,refund_fee,total_fee,notify_url,sign)
        
        Log("Sign %s:"%xml,"local", "0.0.0.0", "DEBUG")

        #res = PostDataWithCert(refund_url, xml.encode('UTF-8'))
        CERT_PATH = "cert/refund_apiclient_cert.pem"
        KEY_PATH = "cert/refund_apiclient_key.pem"

        with requests.Session() as s:
            resp = s.post(refund_url, xml.encode('UTF-8'),cert=(CERT_PATH,KEY_PATH))
            Log("wxOrderRefund resp:%s" % resp.content,"local", "0.0.0.0", "DEBUG")
            xml = ET.fromstring(resp.content)
        
        return_code = xml.find("return_code").text
        res_str = 'success'
        if return_code == "SUCCESS":
            result_code = xml.find("result_code").text
            if result_code != "SUCCESS":
                res_str = xml.find("err_code_des").text
        else:
            res_str = xml.find("return_msg").text
        return res_str
    except Exception, e:
        Log("wxOrderRefund Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        return e
    
    
def OrderRefund(order_id):
    try:
        Log("OrderRefund order_id: %s" % order_id, Type="DEBUG")
        mchid = '1499173302'
        order = OITM.objects.filter(ID=order_id)
        if order:
            order = order[0]
        else:
            return HttpResponse('no order found')
        res = wxOrderRefund(order.AppID,mchid,order.TradeNumber,order.TransactionID,order.TotalAmount,order.TotalAmount,'https://class.ddianke.com/RefundCallback')
 
        if res == "success":
            order.Paid = 3 #应该是，然后回调里再设为3
            order.save()
        return res
    except Exception,e:
        Log("OrderRefund error: %s" %e, Type="DEBUG")
        return e
    
        
def GetOpenId(appid,secret,code):
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code'%(appid,secret,code)
    response = urllib2.urlopen(url) 
    resJSON = response.read().decode("utf8")
    res = json.loads(resJSON)
    if ("errcode" in res.keys()):
        Log("GetOpenId error : %s" % resJSON,"local", "0.0.0.0", "DEBUG")
        return res
    
    #user = wxUserClass(appid,res["openId"])
    Log("unionID : %s" % resJSON,"local", "0.0.0.0", "DEBUG")
    users = wxUser.objects.filter(openID = res["openid"])
    if len(users) > 0:
        user = users[0]
        user.unionID =res["unionid"]
        user.SourceAccount = appid
    else:
        user = wxUser(openID = res["openid"], unionID=res["unionid"], SourceAccount = appid)
    user.save()
    #user.SetUserInfo(json.loads(userInfo))
    #Log("GetOpenId: %s" % res,"local", "0.0.0.0", "DEBUG")
    return res


    
def GetPaidList(productCode,productType):
	oitms = getVar("OITM").filter(ProductCode = productCode, ProductType=productType)
	return oitms

def GetPayUrl(openid, isToday = True):
    url = ''
    try:
        #updateVar("Products")
        if isToday:
            today = datetime(datetime.today().year,datetime.today().month,datetime.today().day, 0 , 0, 0 , 0)
        else:
            today = datetime(datetime.today().year,datetime.today().month,datetime.today().day, 23 , 59, 59 , 0)
            
        articles = getVar("Products").filter(OwnerOpenID = openid, ProductType='article').filter(CreatedTime__gte = today)
        
        if (len(articles) > 0):
            url = articles[len(articles) - 1].PayUrl
        return url
    except Exception, e:
        Log("GetPayUrl Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        return url

        
        
#实际返回值包括个人打赏和文章打赏，不想改方法名了
def GetPaidArticleList(articleid = '', openid = ''):
    try:
        #updateVar('Products')            
        if openid != '':
            articles = getVar("Products").filter(OwnerOpenID = openid).filter(Q(ProductType = 'article') | Q(ProductType = 'owner'))
        else:
            articles = getVar("Products").filter(Q(ProductType = 'article') | Q(ProductType = 'owner'))
        if articleid != '':
            articles = articles.filter(ProductCode = articleid)

        #Log("GetPaidArticleList ids:%s" % ids,"local", "0.0.0.0", "DEBUG")
        oitms = getVar("OITM").filter(Paid = 1).filter(Q(ProductType='article') | Q(ProductType='owner'))
        paidArticles = []
        for article in articles:
            paids = oitms.filter(ProductCode = article.ProductCode)
            sumValue = paids.aggregate(Sum('TotalAmount'))['TotalAmount__sum']
            total = 0
            if sumValue is not None:
                total = sumValue / 100.0
            paidArticles.append({'id':article.ProductCode,'type':article.ProductType,'name':article.ProductName,'author':article.OwnerName,'payurl':article.PayUrl,'paidCount':len(paids),'totalPrice':total, 'openid':article.OwnerOpenID})
                 
        return paidArticles
    except Exception, e:
        Log("GetPaidArticleList Error: %s" % e,"local", "0.0.0.0", "DEBUG")

#支付信息，包括提现信息
def GetPaidProductsWithWithdraw(articleid = '', openid = ''):
    try:
        paidProducts = GetPaidArticleList(articleid, openid)
        
        products = []
        for prod in paidProducts:
            withdrawAmount = 0
            userWithdraw = getVar('BusinessSpending').filter(TargetOpenID = prod['openid'])
            if len(userWithdraw) > 0:
                #Log("GetPaidProductListWithWithdraw withdraw len: %d" % len(userWithdraw) ,"local", "0.0.0.0", "DEBUG")
                withdrawAmount = userWithdraw.aggregate(Sum("Amount"))["Amount__sum"]
            products.append({'id':prod['id'],'type':prod['type'],'name':prod['name'],'author':prod['author'],'payurl':prod['payurl'],'paidCount':prod['paidCount'],'totalPrice':prod['totalPrice'], 'openid':prod['openid'], 'withdrawAmount':withdrawAmount})
        return products
    except Exception, e:
        Log("GetPaidProductListWithWithdraw Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        
        
def GetMiniappAccessToken(needrefresh = False):
    try:
        
        productType = 'owner'
        if not needrefresh and (mc.get("miniapp_access_token") is not None and mc.get("miniapp_access_token_expired") is not None and mc.get("miniapp_access_token_expired") > datetime.today()):
            Log("miniapp token expired:%s" % mc.get("miniapp_access_token_expired"), Type="DEBUG")
        else:
            RefreshMiniappAccessToken()
        token = mc.get("miniapp_access_token")
        return token
    except Exception,e:
        Log("GetMiniappAccessToken error:%s"%e, "local", "0.0.0.0", "DEBUG")
        return None
    
    
def RefreshMiniappAccessToken():
            appid=MINIAPPID
            secret='e07e28bb5edad5140a9d8c2e1558e227'
            token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (appid,secret)
            response = urllib2.urlopen(token_url) 
            res = response.read().decode("utf8") 
            miniapp_access_token = json.loads(res)["access_token"]
            expires_in = json.loads(res)["expires_in"]
            miniapp_access_token_expired = datetime.today() + timedelta(0, 1800 , 0)#expires_in 10分钟去拿一次，看看还会不会过期
            mc.set("miniapp_access_token", miniapp_access_token)
            mc.set("miniapp_access_token_expired", miniapp_access_token_expired )
            Log("miniapp token :%s" % miniapp_access_token, Type="DEBUG")
            Log("miniapp token expired:%s" % expires_in, Type="DEBUG")
        
def CreateWXCodeBase64(page,mini_openid,mini_product_id, count = 0):
    try:
        if count > 0:
            token = GetMiniappAccessToken(True)
        else:
            token = GetMiniappAccessToken()
        #Log("miniapp token :%s" % token, Type="DEBUG")
        wxuser = wxUser.objects.get(openID = mini_openid)
        scene="wxuserid_%d_prodid_%d" % (wxuser.ID, mini_product_id)
        avatar_img = None
        r2 = 120
        if wxuser.Avatar:
            
            Log("avatar %s" % wxuser.Avatar, Type="DEBUG")
            with requests.Session() as s:
                r = s.get(wxuser.Avatar, stream=True)
            temp_storage = io.BytesIO()
            for block in r.iter_content(1024):
                temp_storage.write(block)
            
            avatar_img = Image.open(StringIO.StringIO(temp_storage.getvalue()))
            avatar_img = avatar_img.resize((r2,r2), Image.ANTIALIAS)
            #circle = Image.new('L', (r2,r2), 0)
            #draw = ImageDraw.Draw(circle)
            #draw.ellipse((0, 0, r2, r2), fill=255)
            #alpha = Image.new('L', (r2, r2), 255)
            #alpha.paste(circle, (0, 0))
            #avatar_img.putalpha(alpha)
            buffer = cStringIO.StringIO()
            #avatar_img.save(buffer, format="png")
            #avatar_img = Image.open(cStringIO.StringIO(buffer.getvalue()))
            imb = Image.new('RGBA', (r2, r2),(255,255,255,0))
            pima = avatar_img.load()
            pimb = imb.load()
            r = float(r2/2) #圆心横坐标
            for i in range(r2):
                for j in range(r2):
                    lx = abs(i-r+0.5) #到圆心距离的横坐标
                    ly = abs(j-r+0.5)#到圆心距离的纵坐标
                    l  = pow(lx,2) + pow(ly,2)
                    if l <= pow(r, 2):
                        pimb[i,j] = pima[i,j]
            imb.save(buffer, format="png")
            avatar_img = Image.open(cStringIO.StringIO(buffer.getvalue()))

        url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=%s' % token
        data = {'page':page, 'scene':scene}
        bg = Image.open("static/images/qrcode_bg.jpg")
        im = ImageDraw.Draw(bg)
        font = ImageFont.truetype("static/fonts/simsun.ttc", 34, encoding="utf-8")
        im.text((178,50), wxuser.Name, fill = (0, 0 ,0), font=font)
        #bg.show()
        Log("data :%s" % data, Type="DEBUG")
        r = None
        with requests.Session() as s:
            r = s.post(url,json.dumps(data),stream=True)
        
        temp_storage = io.BytesIO()
        #for block in r.iter_content(1024):
        temp_storage.write(r.content)
        Log("r %d" % len(r.content), Type="DEBUG")
        img = Image.open(StringIO.StringIO(temp_storage.getvalue()))
        out=img.resize((150,150))
        #out=img.rotate(45) #逆时针旋转45度
        bg.paste(avatar_img,(30,30,r2+30,r2+30))
        bg.paste(out, (500, 1000, 650, 1150))
        buffer = cStringIO.StringIO()
        bg.save(buffer, format="jpeg")
        #base64_str = 'data:image/png;base64,%s' % base64.b64encode(buffer.getvalue())

        return buffer.getvalue()
    except Exception, e:
        Log("CreateWXCode Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        res = json.loads(r.content)
        Log("CreateWXCode r: %s" % res,"local", "0.0.0.0", "DEBUG")
        count += 1
        if count < 3:
            return CreateWXCodeBase64(page,mini_openid,mini_product_id,count)
        else:
            return e
        

    
def UpdateExtraInfo(appid, openid, birthday, company, industry, salary, province, city, workDate, university, major, growth):
    try:
        users = getVar('miniappUser').filter(SourceAccount=appid,openID = openid)
        if len(users) >0:
            user = users[0]
            if len(birthday) == 10:
            	user.Birthday =  datetime.strptime(birthday + " 00:00", "%Y-%m-%d %H:%M")
                #y =  time.strptime(birthday, "%Y-%m-%d")
            user.Company = company
            user.Industry = industry
            user.Salary = salary
            user.Province2 = province
            user.City2 = city
            if len(workDate) == 10:
            	user.DateOfFirstJob = datetime.strptime(workDate + " 00:00", "%Y-%m-%d %H:%M")
                #x = time.strptime(workDate, "%Y-%m-%d")
            user.University = university
            user.Major = major
            user.Growth = growth
            user.save()
            updateVar('miniappUser')
        else:
            return 'no user'
    except Exception, e:
        Log("UpdateUserInfo Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        return e
    return 'success'

def CheckVersion(version, page):
    versions = ['2.2.12.4'] #当前在检测的版本，此版本外都将进入topic,当前审核版本'2.2.10.4'
    if version in versions and page == 'topic':
        return True
    else:
        return False

def SaveFormid(openid, formid, nick, ispay = False):
    try:
        if formid is None or formid == '' or formid == 'undefined':
            return 'fail'
        highpoints = re.compile('the formId')
        match = highpoints.match(formid)
        if match:
            return 'fail'
        lastcount = 1
        if ispay:
            lastcount = 3
        f = FormID(OpenID=openid, FID = formid, NickName = nick, LastCount = lastcount, PostTime = datetime.today())
        f.save()

        return 'success'
    except Exception, e:
        Log("SaveFormid Error: %s" % e,"local", "0.0.0.0", "DEBUG")
        return e

def GetFormid(openid):
    formids = FormID.objects.filter(OpenID = openid, LastCount__gt=0).order_by('ID')
    
    if not formids:
        return ''
    res = ''
    indate = timedelta(days=7)
    for item in formids:
        formid = item.FID
        postTime = item.PostTime
        if postTime + indate > datetime.today():
            res = formid
            item.LastCount -= 1
            item.save()
            break
        else:
            item.LastCount = 0
            item.save()
    return res
            
            
def SendTemplateMsg(openid,template_id,paramDic,redirect_url="pages/order-list/index?currentType=2", count=0):
    appid='wxf11978168e04aba2'
    secret='e07e28bb5edad5140a9d8c2e1558e227'
    keys = ['keyword1','keyword2','keyword3','keyword4','keyword5','keyword6']
    try:
        if count > 0:
            token = GetMiniappAccessToken(True);
        else:
            token = GetMiniappAccessToken();
        formid = GetFormid(openid)
        Log("SendTemplateMsg : %s--%s" % (openid,formid),"local", "0.0.0.0", "DEBUG")
        url = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=%s" % token
        params = {
            "touser":openid,
            "template_id":template_id,
            "page": redirect_url,
            "form_id": formid,
            "data":{
                
            }
        }
        for key in keys:
            if paramDic.has_key(key):
                params['data'][key] = {"value":paramDic[key], "color":"#173177"}
        res = Post(url,params)
        Log("SendTemplateMsg miniapp : %s" % res,"local", "0.0.0.0", "DEBUG")
        res = json.loads(res)
        if res['errcode'] == 40001:#41028
            if count < 3:
                count += 1
                res = SendTemplateMsg(openid,template_id,paramDic,count=count)
                
        return res
    except Exception, e:
        Log("SendTemplateMsg openid: %s;  Error: %s" % (openid,e),"local", "0.0.0.0", "DEBUG")
        return e


#支付方法，目前只有打赏提现
def EnterprisePay(appid,amount, openid,mchid, productCode, productType):
    try:
        price = int(amount)
        nonce_str = int(time.time())
        partner_trade_no = nonce_str
        values = {
            "amount": price,
            "check_name": "FORCE_CHECK",
            "desc": "withdraw",
            "mch_appid":appid,
            "mchid":mchid,
            "nonce_str":nonce_str,
            "openid": openid,
            "partner_trade_no":partner_trade_no,
            "re_user_name": "boss",
            "spbill_create_ip": "167.220.232.147"
        }
        sign =GetSign(values)
        
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
        #url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        
        
        xml = """<xml>
	<mch_appid>%s</mch_appid>
	<mchid>%s</mchid>
	<nonce_str>%s</nonce_str>
    <partner_trade_no>%s</partner_trade_no>
    <openid>%s</openid>
	<check_name>FORCE_CHECK</check_name>
	<re_user_name>boss</re_user_name>
	<amount>%s</amount>
    <desc><![CDATA[withdraw]]></desc>
	<spbill_create_ip>167.220.232.147</spbill_create_ip>
	<sign><![CDATA[%s]]></sign>
</xml>"""%(appid, mchid, nonce_str, partner_trade_no, openid,price, sign)
        #%(price, appid, mchid, nonce_str,  openid, partner_trade_no,sign)
        Log("EnterprisePay 1 %s" % xml,"local", "0.0.0.0", "DEBUG")
        
        encodeXML = xml.encode('UTF-8').strip()
  #      encodeXML = """<?xml version="1.0" encoding="utf-8"?><xml>
#	<amount>330</amount>
#	<check_name>FORCE_CHECK</check_name>
#	<desc>withdraw</desc>
#	<mch_appid>wx0c0e0edd8eaad932</mch_appid>
#	<mchid>1415334402</mchid>
#	<nonce_str>1505378461</nonce_str>
#	<openid>oNvgX0WFITP4WESUCPbpUepqOeh0</openid>
#	<partner_trade_no>1505378461</partner_trade_no>
#	<re_user_name>boss</re_user_name>
#	<spbill_create_ip>167.220.232.147</spbill_create_ip>
#	<sign>D23586F08C1BC965099FFDE7BC45C762</sign>
#</xml>""".encode('utf-8').strip()
        certfile = '%s/%s' % (os.path.dirname(__file__),CERTFILE)
        keyfile =  '%s/%s' % (os.path.dirname(__file__),KEYFILE)
        context = ssl.create_default_context()
        context.load_cert_chain(certfile,keyfile)
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
        res = opener.open(url, encodeXML)
        Log("EnterprisePay 2 %s" % res,"local", "0.0.0.0", "DEBUG")
        #filepath = '%s/%s' % (os.path.dirname(__file__),CERTFILE)
        
        #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        http_header = {
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
"X-Requested-With" : "XMLHttpRequest",
"Referer" : "http://applinzi.ddianke.com/",
"Accept-Language" : "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
"Accept-Encoding" :	"gzip, deflate",
"User-Agent" : "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; Touch; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; InfoPath.3)",
"Host" : "applinzi.ddianke.com",
"DNT" : "1",
"Connection" : "Keep-Alive",
"Cache-Control" : "no-cache"
}        
        #req = urllib2.Request(url, encodeXML,http_header )
        #response = urllib2.urlopen(req)
        
        #res = response.read()
        #Log("EnterprisePay 2 %s" % res,"local", "0.0.0.0", "DEBUG")
        
        #resURL = UploadFileFromUrl('xxx%s.xml'%nonce_str,url, encodeXML)
        
        #req = urllib2.Request(url, encodeXML)
        #sock=urllib2.urlopen(req)
        #f=sock.read()
        #stream = cStringIO.StringIO(f)
        #sock.close()
        #bucket = Bucket("image")
        #bucket.put_object('xxx%s.xml'%nonce_str, stream)
        #return_url = bucket.generate_url('xxx%s.xml'%nonce_str)
        
        #Log(return_url,"local", "0.0.0.0", "DEBUG")

        xml = ET.fromstring(res)
        Log(xml,"local", "0.0.0.0", "DEBUG")
        result_code = xml.find("result_code").text
        return_msg = 'SUCCESS'
        Log("EnterprisePay 3","local", "0.0.0.0", "DEBUG")
        if result_code != 'SUCCESS':
            return_msg = xml.find("return_msg").text
            err_code = xml.find("err_code").text
            Log("EnterprisePay err_code:%s" % err_code,"local", "0.0.0.0", "DEBUG")
        else:
            b = BusinessSpending(TradeNo = partner_trade_no, Amount=amount, ProductCode = productCode, ProductType = productType, TargetOpenID = openid)
            b.save()
        Log("EnterprisePay 4","local", "0.0.0.0", "DEBUG")
        return return_msg
    except Exception, e:
        Log("EnterprisePay error:%s" % e,"local", "0.0.0.0", "DEBUG")
        return e

        
def MenuTransform(srcMenu):
    try:
        
        Log("srcMenu loaded as:%s"%srcMenu)
        targetMenu= {
     "button":[] }
        
        for srcButton in srcMenu["selfmenu_info"]["button"]:
            Log("srcButton Parsed: %s" % srcButton)
            targetButton = TransformMenuItem(srcButton)
            targetMenu["button"].append(targetButton)
            Log("targetButton Got: %s" % targetButton)
            
        return targetMenu
    except Exception, e:
        Log("MenuTransform Error: %s" % e)
        
def TransformMenuItem(srcButton, ):
    try:
        Log("Start Transform Menu:%s" % srcButton)
        targetButton = {}
        targetButton["name"] = srcButton["name"]
        if "sub_button" in srcButton.keys():
            buttons = []
            for srcSub_button in srcButton["sub_button"]["list"]:
                targetSub_button = TransformMenuItem(srcSub_button)
                targetSub_button["sub_button"]=[]
                buttons.append(targetSub_button)
            targetButton["sub_button"] = buttons
            return targetButton
        if "type" in srcButton.keys():
            Log("Start Transform Menu type: %s"% srcButton["type"])
            operator = {'text': ToTextButton, 'img':ToImageButton, 'news':ToNewsButton, 'view': ToViewButton, 'voice': ToVoiceButton }
            return operator.get(srcButton["type"])(srcButton)
    except Exception, e:
        Log("TransformMenuItem Error:%s" % e)
        
        
def ToTextButton(srcButton):
    return None

def ToImageButton(srcButton):
    targetButton = {}
    targetButton["name"] = srcButton["name"]
    targetButton["type"] = "media_id"
    targetButton["media_id"] = srcButton["value"]
    return targetButton

def ToNewsButton(srcButton):
    targetButton = {}
    targetButton["name"] = srcButton["name"]
    targetButton["type"] = "media_id"
    targetButton["media_id"] = GetNewsMediaID(srcButton["news_info"]["list"][0]["content_url"])
    return targetButton

def GetNewsMediaID(url):
    #content_url = 
    c = Articles.objects.filter(ArticleURL = url)
    Log("GetNewsMediaID:%s" % len(c))
    if (len(c)==0): 
        return None
    else:
        return c[0].MediaID

def ToViewButton(srcButton):
    try:
        Log("Start ToViewButton: %s" % srcButton)
        targetButton = {}
        targetButton["name"] = srcButton["name"]
        targetButton["type"] = "view"
        targetButton["url"] = srcButton["url"]
        return targetButton
    except Exception, e:
        Log("ToViewButton Error:%s" % e)
    

def ToVoiceButton(srcButton):
    return None


    
    
def BuildIndex(appid):
    Log("Building Index of %s:" % appid)
    if len(wxAccounts.objects.filter(appId = appid))>0:
        wxObj = wxAccounts.objects.filter(appId = appid)[0]
        testWxAccount = wxAccountInterface(wxObj)
        testWxAccount.BuildIndex()
        #testWxAccount.BuildMenu()
    else:
        wxObj = None
    
"""
关于Crypto.Cipher模块，ImportError: No module named 'Crypto'解决方案
请到官方网站 https://www.dlitz.net/software/pycrypto/ 下载pycrypto。
下载后，按照README中的“Installation”小节的提示进行pycrypto安装。
"""
class FormatException(Exception):
    pass

def throw_exception(message, exception_class=FormatException):
    """my define raise exception function"""
    raise exception_class(message)

class SHA1:
    """计算公众平台的消息签名接口"""

    def getSHA1(self, token, timestamp, nonce, encrypt):
        """用SHA1算法生成安全签名
        @param token:  票据
        @param timestamp: 时间戳
        @param encrypt: 密文
        @param nonce: 随机字符串
        @return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update("".join(sortlist))
            return  ierror.WXBizMsgCrypt_OK, sha.hexdigest()
        except Exception,e:
            #print e
            return  ierror.WXBizMsgCrypt_ComputeSignature_Error, None


class XMLParse:
    """提供提取消息格式中的密文及生成回复消息格式的接口"""

    # xml消息模板
    AES_TEXT_RESPONSE_TEMPLATE = """<xml>
<Encrypt><![CDATA[%(msg_encrypt)s]]></Encrypt>
<MsgSignature><![CDATA[%(msg_signaturet)s]]></MsgSignature>
<TimeStamp>%(timestamp)s</TimeStamp>
<Nonce><![CDATA[%(nonce)s]]></Nonce>
</xml>"""

    def extract(self, xmltext):
        """提取出xml数据包中的加密消息
        @param xmltext: 待提取的xml字符串
        @return: 提取出的加密消息字符串
        """
        try:
            xml_tree = ET.fromstring(xmltext)
            encrypt  = xml_tree.find("Encrypt")
            #try:
            #    touser_name = xml_tree.find("ToUserName")
            #except Exception, e:
            #    touser_name = "null"
            return  ierror.WXBizMsgCrypt_OK, encrypt.text
        except Exception,e:
            #print e
            return  ierror.WXBizMsgCrypt_ParseXml_Error,None,None

    def generate(self, encrypt, signature, timestamp, nonce):
        """生成xml消息
        @param encrypt: 加密后的消息密文
        @param signature: 安全签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 生成的xml字符串
        """
        resp_dict = {
                    'msg_encrypt' : encrypt,
                    'msg_signaturet': signature,
                    'timestamp'    : timestamp,
                    'nonce'        : nonce,
                     }
        resp_xml = self.AES_TEXT_RESPONSE_TEMPLATE % resp_dict
        return resp_xml


class PKCS7Encoder():
    """提供基于PKCS7算法的加解密接口"""

    block_size = 32
    def encode(self, text):
        """ 对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def decode(self, decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = ord(decrypted[-1])
        if pad<1 or pad >32:
            pad = 0
        return decrypted[:-pad]


class Prpcrypt(object):
    """提供接收和推送给公众平台消息的加解密接口"""

    def __init__(self,key):
        #self.key = base64.b64decode(key+"=")
        self.key = key
        # 设置加解密模式为AES的CBC模式
        self.mode = AES.MODE_CBC


    def encrypt(self,text,appid):
        """对明文进行加密
        @param text: 需要加密的明文
        @return: 加密得到的字符串
        """
        # 16位随机字符串添加到明文开头
        text = self.get_random_str() + struct.pack("I",socket.htonl(len(text))) + text + appid
        # 使用自定义的填充方式对明文进行补位填充
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        # 加密
        cryptor = AES.new(self.key,self.mode,self.key[:16])
        try:
            ciphertext = cryptor.encrypt(text)
            # 使用BASE64对加密后的字符串进行编码
            return ierror.WXBizMsgCrypt_OK, base64.b64encode(ciphertext)
        except Exception,e:
            #print e
            return  ierror.WXBizMsgCrypt_EncryptAES_Error,None

    def decrypt(self,text,appid):
        """对解密后的明文进行补位删除
        @param text: 密文
        @return: 删除填充补位后的明文
        """
        try:
            cryptor = AES.new(self.key,self.mode,self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text  = cryptor.decrypt(base64.b64decode(text))
        except Exception,e:
            #print e
            return  ierror.WXBizMsgCrypt_DecryptAES_Error,None
        try:
            pad = ord(plain_text[-1])
            # 去掉补位字符串
            #pkcs7 = PKCS7Encoder()
            #plain_text = pkcs7.encode(plain_text)
            # 去除16位随机字符串
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack("I",content[ : 4])[0])
            xml_content = content[4 : xml_len+4]
            from_appid = content[xml_len+4:]
        except Exception,e:
            #print e
            return  ierror.WXBizMsgCrypt_IllegalBuffer,None
        if  from_appid != appid:
            return ierror.WXBizMsgCrypt_ValidateAppid_Error,None
        return 0,xml_content

    def get_random_str(self):
        """ 随机生成16位字符串
        @return: 16位字符串
        """
        rule = string.letters + string.digits
        str = random.sample(rule, 16)
        return "".join(str)

class WXBizMsgCrypt(object):
    #构造函数
    #@param sToken: 公众平台上，开发者设置的Token
    # @param sEncodingAESKey: 公众平台上，开发者设置的EncodingAESKey
    # @param sAppId: 企业号的AppId
    def __init__(self,sToken,sEncodingAESKey,sAppId):
        try:
            self.key = base64.b64decode(sEncodingAESKey+"=")
            assert len(self.key) == 32
        except:
            throw_exception("[error]: EncodingAESKey unvalid !", FormatException)
           #return ierror.WXBizMsgCrypt_IllegalAesKey)
        self.token = sToken
        self.appid = sAppId

    def EncryptMsg(self, sReplyMsg, sNonce, timestamp = None):
        #将公众号回复用户的消息加密打包
        #@param sReplyMsg: 企业号待回复用户的消息，xml格式的字符串
        #@param sTimeStamp: 时间戳，可以自己生成，也可以用URL参数的timestamp,如为None则自动用当前时间
        #@param sNonce: 随机串，可以自己生成，也可以用URL参数的nonce
        #sEncryptMsg: 加密后的可以直接回复用户的密文，包括msg_signature, timestamp, nonce, encrypt的xml格式的字符串,
        #return：成功0，sEncryptMsg,失败返回对应的错误码None
        pc = Prpcrypt(self.key)
        ret,encrypt = pc.encrypt(sReplyMsg, self.appid)
        if ret != 0:
            return ret,None
        if timestamp is None:
            timestamp = str(int(time.time()))
        # 生成安全签名
        sha1 = SHA1()
        ret,signature = sha1.getSHA1(self.token, timestamp, sNonce, encrypt)
        if ret != 0:
            return ret,None
        xmlParse = XMLParse()
        return ret,xmlParse.generate(encrypt, signature, timestamp, sNonce)

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        # 检验消息的真实性，并且获取解密后的明文
        # @param sMsgSignature: 签名串，对应URL参数的msg_signature
        # @param sTimeStamp: 时间戳，对应URL参数的timestamp
        # @param sNonce: 随机串，对应URL参数的nonce
        # @param sPostData: 密文，对应POST请求的数据
        #  xml_content: 解密后的原文，当return返回0时有效
        # @return: 成功0，失败返回对应的错误码
         # 验证安全签名
        xmlParse = XMLParse()
        ret,encrypt = xmlParse.extract(sPostData)
        if ret != 0:
            return ret, None
        sha1 = SHA1()
        ret,signature = sha1.getSHA1(self.token, sTimeStamp, sNonce, encrypt)
        if ret  != 0:
            return ret, None
        if not signature == sMsgSignature:
            return ierror.WXBizMsgCrypt_ValidateSignature_Error, None
        pc = Prpcrypt(self.key)
        ret,xml_content = pc.decrypt(encrypt,self.appid)
        return ret,xml_content
 