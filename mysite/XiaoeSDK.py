# -*- coding:utf-8 -*-  
import sys 
import json
import time
import collections
import hashlib
import urllib
import urllib2


reload(sys) 
sys.setdefaultencoding('utf8')

class XiaoeSDK(object):
    def __init__(self, app_id, app_secret):
        self.__app_id = app_id;
        self.__app_secret = app_secret;
        self.__use_type = 0;

    #发送请求
    def send(self, cmd, paramsArray, use_type = 0, version = '1.0'):
        self.__use_type = use_type;
        url = 'http://api.xiaoe-tech.com/open/';
        url = url + cmd + '/' + version;
        jsonPostData = self.__getEncodedData(paramsArray);

        headers = {'Content-type': 'application/json; charset=utf-8'};
        req = urllib2.Request(url, jsonPostData, headers);
        response = urllib2.urlopen(req);
        try:
            result = response.read();
            resultJson = json.loads(result, encoding="UTF-8");
 
            if 'code' in resultJson and 'data' in resultJson and resultJson['code'] == 0 and isinstance(resultJson['data'], list):
                resultJson = self.__getDecodedData(resultJson);
            return resultJson;
        except ValueError, e:
            return 'json parse error ' + e.message;
    
    #获取解码结果
    def __getDecodedData(self, jsonData):
        if 'app_id' in jsonData and jsonData['app_id'] != self.__app_id:
            return {'code':'100','msg':'服务器返回app_id异常','data':[]};
        else:
            if 'sign' not in jsonData:
                return {'code':'100','msg':'加密串校验出错','data':[]};

            code = jsonData['code'] if 'code' in jsonData else '';
            msg = jsonData['msg'] if 'msg' in jsonData else '';
            data = jsonData['data'] if 'data' in jsonData else '';

            return {'code':code,'msg':msg,'data':data};
    
    #对输入的参数进行打包并json处理
    def __getEncodedData(self, data):
        paramsDict = {};

        paramsDict['data'] = data;
        paramsDict['timestamp'] = int(time.time());
        paramsDict['app_id'] = self.__app_id;
        paramsDict['use_type'] = self.__use_type;
        md5Str = self.__createSign(paramsDict);
        paramsDict['sign'] = md5Str;

        return json.dumps(paramsDict, separators=(',', ':'), ensure_ascii=False);
    
    # 排序
    def __sortDict(self, data, ascending = True):
        if ascending:
            return collections.OrderedDict(sorted(data.items()));
        else:
            return collections.OrderedDict(sorted(data.items(), reverse=True));

    #加密方法
    def __createSign(self, data):
        #根据键名对字典序进行排序
        orderedData = self.__sortDict(data);
        rawData = [];
        strs = '';

        for (key,value) in orderedData.items():
            if type(value) == str or type(value) == int or type(value) == bool or type(value) == float:
                strs = str(value);
            else:
                strs = json.dumps(value,separators=(',', ':'), ensure_ascii=False); 
            strs = key + '=' + strs;
            rawData.append(strs);

        strs = 'app_secret=' + self.__app_secret;
        rawData.append(strs);
        rawString = '&'.join(rawData);

        return self.__getMd5LowerStr(rawString);
    
    #根据输入得到md5的值，并转成小写字母的形式
    def __getMd5LowerStr(self, string):
        m = hashlib.md5();
        m.update(string);
        sign = m.hexdigest();
        return sign.lower();