#  -*- coding: utf-8 -*-
import records
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from tg import Tg


class Youla:
    """docstring"""

    def __init__(self, task):
        """Constructor"""
        self.__task = task  # protected
        # Инициализируем базу
        self.__db = self.__prepare_db(task["database"])
        # Инициализируем бота для Telegram
        if "proxy" in task:
            self.__tg = Tg(task["tgBotKey"], task["proxy"])
        else:
            self.__tg = Tg(task["tgBotKey"])

    def __prepare_db(self,link):
        db = records.Database(link)
        conn = db.get_connection()
        with conn:
            conn.query('Create table if not exists YOULA  (tag VARCHAR(255), link VARCHAR(255),price VARCHAR(20))')
        return db


    def __check_record(self,record):
        conn = self.__db.get_connection()
        with conn:
            rows = conn.query(
                "select link from YOULA where tag='{}' and link='{}' and price='{}'".format(record['tag'], record['link'],
                                                                                            record['price']), fetchall=True)
            if len(rows) == 0:
                # Пишем в базу
                conn.query("insert into YOULA (tag,link,price) values('{}','{}','{}')"
                         .format(record['tag'], record['link'], record['price']))
        return len(rows)


    def grab(self):
        ua = UserAgent()
        header = {'User-Agent': str(ua.chrome), 'Accept-Encoding': 'utf-8'}
        task = self.__task
        tag = task["tag"]
        base_url = "https://youla.io"
        searchUrl = task["search"]
        result = requests.get(base_url + searchUrl, headers=header)
        content = result.text
        soup = BeautifulSoup(content, "html.parser")
        advert = soup.find_all("li", "product_item")
        for ad in advert:
            itemLink = base_url + ad.findNext("a")['href']
            itemPrice = self.__getText(ad.find("div", "product_item__description")).replace(' ','')
            # Нашли цену и url, можем писать в базу
            record = dict()
            record['tag'] = tag
            record['link'] = itemLink
            record['price'] = itemPrice
            print("link: {} price: {}".format(record['link'], record['price']))
            if self.__check_record(record) == 0:
                print("new record")
                message = "{} price: {}".format(itemLink, itemPrice)
                self.__tg.send_message(task["tgBotKey"], task["tgChannelId"], message)
            else:
                pass

    def __getText(self,parent):
        return ''.join(parent.find_all(text=True, recursive=False)).strip()