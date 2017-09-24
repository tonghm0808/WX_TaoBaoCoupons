#-*- coding:utf-8 -*-
import bottle
import hashlib
import xml.etree.ElementTree as ET
import time
import pymongo

db_name = 'dwADfZdbrNknnSLAmPxt'
api_key = '48085b6296ac48acb99e6ff71e863630'
secret_key = 'dbd3fcb2c6034b4986364603334d6ffe'
app = bottle()


@app.get('/')
def checkSignature():
    token = "tonghuanmingdeweixin"
    signature = app.request.GET.get('signature', None)
    timestamp = app.request.GET.get('timestamp', None)
    nonce = app.request.GET.get('nonce', None)
    echostr = app.request.GET.get('echostr', None)
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return echostr
    else:
        return False


def parse_msg():
    recvmsg = app.request.body.read()
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg


@app.post("/")
def response_msg():
    # con = pymongo.MongoClient('mongo.duapp.com', 8908)
    # db = con['db_name']
    # db.authenticate(api_key, secret_key)
    # coupons = db['coupons']
    msg = parse_msg()
    # result = coupons.find(
    #     {"title": {"$regex": "%s" % msg['Content']}}, {'_id': 0}).limit(5)
    # con.close()
    echostr = """<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[%s]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>""" % (msg['FromUserName'], msg['ToUserName'], time.time(), "text", '没有结果')
    return echostr


if __name__ == "__main__":
    app.debug(True)
    app.run(host='127.0.0.1', port=8080, reloader=True)

else:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
