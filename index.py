# -*- coding:utf-8 -*-

from bottle import Bottle, request, run, debug
import pymongo
import hashlib
import xml.etree.ElementTree as ET
import time
import re

DB_NAME = 'dwADfZdbrNknnSLAmPxt'
DB_API_KEY = '48085b6296ac48acb99e6ff71e863630'
DB_SECRET_KEY = 'dbd3fcb2c6034b4986364603334d6ffe'

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
    <item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[]]></Description>
    <PicUrl><![CDATA[]]></PicUrl>
    <Url><![CDATA[%s%s]]></Url>
    </item>
    </Articles>
    </xml>'''

item = '''<item>
    <Title><![CDATA[%s%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    <Url><![CDATA[%s]]></Url>
    </item>'''

app = Bottle()


def parse_msg():
    recvmsg = request.body.read()
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg


def search_db(temp=None, num=5):
    temp_list = temp.split(' ')
    con = pymongo.MongoClient('mongo.duapp.com', 8908)
    db = con[DB_NAME]
    db.authenticate(DB_API_KEY, DB_SECRET_KEY)
    result = []
    if len(temp_list) > 1:
        pattern = re.compile('.*?%s.*?%s|.*?%s.*?%s' % (
            temp_list[0], temp_list[1], temp_list[1], temp_list[0]))
        db_result = db['coupons'].find(
            {'title': {'$regex': pattern}}).hint('title').limit(num).sort('biz30Day', -1)
    else:
        pattern = re.compile('%s' % temp_list[0])
        db_result = db_result = db['coupons'].find(
            {'title': {'$regex': pattern}}).hint('title').limit(num).sort('biz30Day', -1)

    for x in db_result:
        result.append(x)
    return result


@app.get('/search')
def search():
    ret = ''
    item = request.query.item
    result = search_db(item, 100)
    if len(result) is 0:
        return '没有搜索到结果！'
    else:
        for i in result:
            p = '<p>%s  %s</p>' % (i['title'], i['shareUrl'])
            ret = ret + p
        return ret


@app.get('/weixin')
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


@app.post("/weixin")
def response_msg():
    msg = parse_msg()
    get_infos = search_db(msg['Content'])
    length = len(get_infos)
    items = ''
    temp = ''

    if length:
        for info in get_infos:
            description = u'【原价%s元 领%s元券】' % (
                info['reservePrice'], info['couponPrice'])
            temp = item % (description,
                           info['title'],
                           description,
                           info['picUrl'],
                           info['shareUrl'])
            items = items + temp

        echostr = pictextTpl % (msg['FromUserName'],
                                msg['ToUserName'],
                                str(int(time.time())),
                                str(length + 1),
                                items,
                                '点击查看更多搜索结果>>>',
                                'http://taoyouquan.duapp.com/search?item=',
                                msg['Content'])
    else:
        echostr = textTpl % (msg['FromUserName'],
                             msg['ToUserName'],
                             str(int(time.time())),
                             msg['MsgType'],
                             '没有搜到结果，请换个关键字搜索！多个关键字之间请用空格分开！\n例如：\n    苹果 数据线\n    家用 吸尘器')
    return echostr


if __name__ == '__main__':
    debug(True)
    run(app, host='127.0.0.1', port=8080, reloader=True)

else:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
