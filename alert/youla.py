#  -*- coding: utf-8 -*-
import records
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from alert.tg import send_message


def prepare_db(link):
    db = records.Database(link)
    conn = db.get_connection()
    with conn:
        conn.query('Create table if not exists YOULA  (tag VARCHAR(255), link VARCHAR(255),price VARCHAR(20))')
    return db


def check_record(db, record):
    conn = db.get_connection()
    with conn:
        rows = db.query(
            "select link from YOULA where tag='{}' and link='{}' and price='{}'".format(record['tag'], record['link'],
                                                                                        record['price']), fetchall=True)
        if len(rows) == 0:
            # Пишем в базу
            db.query("insert into YOULA (tag,link,price) values('{}','{}','{}')"
                     .format(record['tag'], record['link'], record['price']))
    return len(rows)


def grab(task):
    ua = UserAgent()
    print(ua.chrome)
    header = {'User-Agent': str(ua.chrome), 'Accept-Encoding': 'utf-8'}
    print(header)
    db = prepare_db(task["database"])
    tag = task["tag"]
    base_url = "https://youla.io"
    searchUrl = task["search"]
    result = requests.get(base_url + searchUrl, headers=header)
    content = result.text
    soup = BeautifulSoup(content, "html.parser")
    advert = soup.find_all("li", "product_item")
    for ad in advert:
        itemLink = base_url + ad.findNext("a")['href']
        itemPrice = getText(ad.find("div", "product_item__description")).replace(' ','')
        # Нашли цену и url, можем писать в базу
        record = dict()
        record['tag'] = tag
        record['link'] = itemLink
        record['price'] = itemPrice
        print("link: {} price: {}".format(record['link'], record['price']))
        if check_record(db, record) == 0:
            print("new record")
            message = "{} price: {}".format(itemLink, itemPrice)
            send_message(task["tgBotKey"], task["tgChannelId"], message)
        else:
            pass

def getText(parent):
    return ''.join(parent.find_all(text=True, recursive=False)).strip()