# -*- coding:utf-8 -*-

from bottle import Bottle, request, run, debug
import pymongo
import hashlib
import xml.etree.ElementTree as ET
import time

app = Bottle()


@app.get('/')
def checkSignature():
    token = "tonghuanmingdeweixin"
    signature = request.GET.get('signature', None)
    timestamp = request.GET.get('timestamp', None)
    nonce = request.GET.get('nonce', None)
    echostr = request.GET.get('echostr', None)
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return echostr
    else:
        return False


def parse_msg():
    recvmsg = request.body.read()
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg


def search_db(temp=None):
    db_name = 'dwADfZdbrNknnSLAmPxt'
    api_key = '48085b6296ac48acb99e6ff71e863630'
    secret_key = 'dbd3fcb2c6034b4986364603334d6ffe'

    con = pymongo.MongoClient('mongo.duapp.com', 8908)
    db = con[db_name]
    db.authenticate(api_key, secret_key)
    result = []
    for x in db['coupons'].find({"title": {"$regex": temp}}).limit(8).sort('biz30Day', -1):
        result.append(x)
    return result


@app.post("/")
def response_msg():
    msg = parse_msg()
    textTpl = '''<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[%s]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <FuncFlag>0</FuncFlag>
    </xml>'''

    pictextTpl = '''<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>%s</ArticleCount>
    <Articles>
    %s
    </Articles>
    </xml>'''

    item = '''<item>
    <Title><![CDATA[%s%s]]></Title> 
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    <Url><![CDATA[%s]]></Url>
    </item>'''

    get_info = search_db(msg['Content'])
    items = ''
    temp = ''
    length = len(get_info)

    if length:
        for i in range(0, length):
            description = u'【原价%s 券后%s】' % (
                get_info[i]['reservePrice'], get_info[i]['discountPrice'])
            temp = item % (description,
                           get_info[i]['title'],
                           description,
                           get_info[i]['picUrl'],
                           get_info[i]['shareUrl'])
            items = items + temp

        echostr = pictextTpl % (msg['FromUserName'],
                                msg['ToUserName'],
                                str(int(time.time())),
                                str(length),
                                items)
    else:
        echostr = textTpl % (msg['FromUserName'],
                             msg['ToUserName'],
                             str(int(time.time())),
                             msg['MsgType'],
                             '没有搜到结果，请换个关键字搜索！')
    return echostr


if __name__ == '__main__':
    debug(True)
    run(app, host='127.0.0.1', port=8080, reloader=True)

else:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
