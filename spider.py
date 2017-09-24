# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import time
import pymongo

db_name = 'dwADfZdbrNknnSLAmPxt'
con = pymongo.MongoClient('mongo.duapp.com', 8908)
db = con['db_name']
api_key = '48085b6296ac48acb99e6ff71e863630'
secret_key = 'dbd3fcb2c6034b4986364603334d6ffe'
db.authenticate(api_key, secret_key)
coupons = db['coupons']

header = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
}
url = 'https://m.lapin365.com/index/GetHomeListAjax'


def get_goods(url, page=1, data=None):
    payload = {'limit': 10, 'pageIndex': page, 'clienttype': 0}
    wb_data = requests.post(url, data=payload, headers=header)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    titles = soup.select('li > a.couponlink.pic-wrap')
    links = soup.select('li > a.couponlink.pic-wrap')
    imgs = soup.select('li > a.couponlink.pic-wrap > img.lazy')
    originprices = soup.select('div.salesinfo > del.origin-price')
    discountprices = soup.select('span.aftercoupon > span')

    if data is None:
        for title, link, img, originprice, discountprice in zip(titles, links, imgs, originprices, discountprices):
            data = {
                'title': title.get('title'),
                'link': link.get('data-couponbuylink'),
                'img': img.get('data-original'),
                'originprice': originprice.get_text()[1:-1],
                'discountprice': discountprice.get_text(),
            }
            coupons.insert_one(data)
            print data
    return data


page_num = 1
while(1):
    res = get_goods(url, page_num)
    if res is None:
        break
    else:
        page_num = page_num + 1
    time.sleep(1)
