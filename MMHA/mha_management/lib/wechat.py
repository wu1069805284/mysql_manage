#!/usr/bin/env python
#coding=utf-8
#create by wuweijian
from detection import getConfig
from LogHandler import WriteLog
import urllib2,json,sys


def getMsg(msg):
    reload(sys)
    sys.setdefaultencoding('utf8')
    return msg

def userinfo():
    luser=getConfig('wechat_user','we_user')
    userlist=luser.replace(',','|')
    return  userlist


def minwechat(msg):
    Log=WriteLog()
    CropID='wwe05d1ee60267cbdb'
    Secret='K2M9bfrNrtNSIB4zWckNpnPXoZhf8_UcIRDK81SHtik'
    GURL="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (CropID,Secret)
    result=urllib2.urlopen(urllib2.Request(GURL)).read()
    dict_result = json.loads(result)
    Gtoken=dict_result['access_token']
    PURL="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Gtoken
    post_data = {}
    msg_content = {}
    msg_content['content'] = getMsg(msg)
    post_data['touser'] = userinfo()
    post_data['toparty'] = ""
    post_data['msgtype'] = 'text'
    post_data['agentid'] = '1000002'
    post_data['text'] = msg_content
    post_data['safe'] = '0'
    json_post_data = json.dumps(post_data,False,False)
    request_post = urllib2.urlopen(PURL,json_post_data)
    result=request_post.read()
    if eval(result)['errmsg'] == 'ok':
        return 1
    else:
        info=eval(result)['errmsg']
        Log.write('e'," 微信发送失败: {}".format(info))
        return 2

if __name__ == '__main__':
    minwechat('测试')
