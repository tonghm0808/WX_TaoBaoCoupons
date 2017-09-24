# -*- coding:utf-8 -*-

from bottle import Bottle
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


def con_db():
    db_name = 'dwADfZdbrNknnSLAmPxt'
    api_key = '48085b6296ac48acb99e6ff71e863630'
    secret_key = 'dbd3fcb2c6034b4986364603334d6ffe'

    con = pymongo.MongoClient('mongo.duapp.com', 8908)
    db = con[db_name]
    if db.authenticate(api_key, secret_key) is True:
        db['coupons'].insert({"id": 10, 'value': "test test"})
        return True
    else:
        return False


@app.post("/")
def response_msg():
    msg = parse_msg()
    textTpl = """<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[%s]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>"""
    get_db_info = con_db()
    if get_db_info is True:
        echostr = textTpl % (msg['FromUserName'],
                             msg['ToUserName'], str(int(time.time())), msg['MsgType'], '加入成功')
    else:
        echostr = textTpl % (msg['FromUserName'],
                             msg['ToUserName'], str(int(time.time())), msg['MsgType'], '加入失败')
    return echostr


if __name__ == '__main__':
    debug(True)
    run(app, host='127.0.0.1', port=8080, reloader=True)

else:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
