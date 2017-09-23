#-*- coding:utf-8 -*-
from bottle import *
import hashlib
import xml.etree.ElementTree as ET
import urllib2
import json
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


@app.post("/")
def response_msg():
    msg = parse_msg()
    echostr = """<xml> 
    <ToUserName><![CDATA[%s]]></ToUserName> 
    <FromUserName><![CDATA[%s]]></FromUserName> 
    <CreateTime>%s</CreateTime> 
    <MsgType><![CDATA[%s]]></MsgType> 
    <Content><![CDATA[%s]]></Content> 
    </xml>""" % (msg['FromUserName'], msg['ToUserName'], time.time(), "text", msg['Content'])
    return echostr


if __name__ == "__main__":
    debug(True)
    run(app, host='127.0.0.1', port=8080, reloader=True)

else:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
