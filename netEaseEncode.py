# -*- coding: utf-8 -*-
# 加密参数相关。
# 具体http://s3.music.126.net/sep/s/2/core.js?5d6f8e4d01b4103ec9f246a2ef70e6d1在这个js中可以查看。
# 好吧，其实不用分析这个js，在这个git中可以找到https://github.com/xiyouMc/ncmbot，不过他是for python2的。
# 针对pyton3做了修改。
import json
import base64
import random
import requests
from Crypto.Cipher import AES


modulu = '00e0b509f6259df8642dbc35662901477df22677ec152b5\
ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f\
56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3\
685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef527\
41d546b8e289dc6935b3ece0462db0a22b8e7'


nonce = b'0CoJUm6Qyw8W8jud'
pubKey = '010001'
param = {'ids': '', 'br': 999000, 'csrf_token': ''}
url = "http://music.163.com/weapi/song/enhance/player/url"


def aesEncrypt(text, secKey):

    pad = 16 - len(text) % 16

    # aes加密需要byte类型。
    # 因为调用两次，下面还要进行补充位数。
    # 直接用try与if差不多。

    try:
        text = text.decode()
    except:
        pass

    text = text + pad * chr(pad)
    try:
        text = text.encode()
    except:
        pass

    encryptor = AES.new(secKey, 2, b'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def createSecretKey(size):
    # os.urandom返回是个字符串。
    # 不过加密的目的是需要一个字符串。
    # 因为密钥之后会被加密到rsa中一起发送出去。
    # 所以即使是个固定的密钥也是可以的。

    # return (''.join(map(lambda xx: (hex(ord(xx))[2:]),
    # os.urandom(size))))[0:16]
    return ''.join(random.sample('1234567890qwertyuipasdfghjklzxcvbnm', 16))


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(text.encode('hex'), 16)**int(pubKey, 16) % int(modulus, 16)

    return format(rs, 'x').zfill(256)


def encrypted_request(text):

    # 这边是加密过程。
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulu)
    # 在那个js中也可以找到。

    # params加密后是个byte，解下码。
    data = {'params': encText.decode(), 'encSecKey': encSecKey}
    return data


def get_url(text):
    ids = text.split('=')[1]
    param['ids'] = '[' + ids + ']'
    data = encrypted_request(param)
    html = requests.post(url, data=data).json()
    return html['data'][0]['url']


# print get_url('http://music.163.com/#/song?id=210991')
