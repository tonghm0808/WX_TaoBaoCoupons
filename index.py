# -*- coding:utf-8 -*-

from bottle import Bottle, request, view
from bae.core.wsgi import WSGIApplication
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


@app.route('/weixin', method=['GET', 'POST'])
def weixin():
    if request.method == 'GET':
        token = "tonghuanming"
        signature = request.query.signature
        timestamp = request.query.timestamp
        nonce = request.query.nonce
        echostr = request.query.echostr
        tmpList = [token, timestamp, nonce]
        tmpList.sort()
        tmpstr = "%s%s%s" % tuple(tmpList)
        hashstr = hashlib.sha1(tmpstr).hexdigest()
        if hashstr == signature:
            return echostr
        else:
            return False
    else:
        recvmsg = request.body.read()
        root = ET.fromstring(recvmsg)

        get_infos = search_db(root.find('Content').text)
        length = len(get_infos)

        if length:
            items = ''
            temp = ''
            for info in get_infos:
                description = u'【原价%s元 领%s元券】' % (
                    info['reservePrice'], info['couponPrice'])
                temp = item % (description,
                               info['title'],
                               description,
                               info['picUrl'],
                               info['shareUrl'])
                items = items + temp

            echostr = pictextTpl % (root.find('FromUserName').text,
                                    root.find('ToUserName').text,
                                    str(int(time.time())),
                                    str(length + 1),
                                    items,
                                    u'点击查询更多搜索结果>>>',
                                    u'http://taoyouquan.duapp.com/search?item=',
                                    root.find('Content').text)
        else:
            echostr = textTpl % (root.find('FromUserName').text,
                                 root.find('ToUserName').text,
                                 str(int(time.time())),
                                 root.find('MsgType').text,
                                 u'没有搜到结果，请换个关键字搜索！多个关键字之间请用空格分开！\n例如：\n    苹果 数据线\n    家用 吸尘器')

        return echostr


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


@app.route('/search', methods='GET')
def search():
    ret = ''
    item = request.query.item
    result = search_db(item, 100)
    if len(result) is 0:
        return '没有搜索到结果！'
    else:
        for i in result:
            p = '<p><a href="%s">%s</a></p>' % (i['shareUrl'], i['title'])
            ret = ret + p
        return ret

    # if __name__ == '__main__':
    #     debug(True)
    #     run(app, host='127.0.0.1', port=8080, reloader=True)

    # else:
    #     from bae.core.wsgi import WSGIApplication
    #     application = WSGIApplication(app)


application = WSGIApplication(app)
