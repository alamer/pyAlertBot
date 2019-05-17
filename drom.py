#  -*- coding: utf-8 -*-
import re

import records
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from tg import Tg


class Drom:
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

    def __prepare_db(self, link):
        db = records.Database(link)
        conn = db.get_connection()
        with conn:
            conn.query(
                'Create table if not exists DROM (tag VARCHAR(255),link VARCHAR(255),price VARCHAR(20))')
        return db

    def __check_record(self, avito_record):
        conn = self.__db.get_connection()
        with conn:
            rows = conn.query(
                "select price from DROM where tag='{}' and link='{}'".format(avito_record['tag'], avito_record['link']),
                fetchall=True)
            if len(rows) == 0:
                # new item
                conn.query("insert into DROM (tag,link,price) values('{}','{}','{}')"
                           .format(avito_record['tag'], avito_record['link'],
                                   avito_record['price']))
                res = {'message': "New", 'icon': '✅'}
            elif int(rows[0]['price']) > int(avito_record['price']):
                # item changed, price down
                conn.query("update DROM set price='{}' where tag='{}' and link='{}'".format(avito_record['price'],
                                                                                            avito_record['tag'],
                                                                                            avito_record['link']))
                res = {'message': "Price down", 'icon': '👍', 'oldPrice': rows[0]['price']}
            elif int(rows[0]['price']) < int(avito_record['price']):
                # item changed, price up
                conn.query("update DROM set price='{}' where tag='{}' and link='{}'".format(avito_record['price'],
                                                                                            avito_record['tag'],
                                                                                            avito_record['link']))
                res = {'message': "Price up", 'icon': '👎', 'oldPrice': rows[0]['price']}
            else:
                # price not changed
                res = None
        return res

    def grab(self):
        ua = UserAgent()
        header = {'User-Agent': str(ua.chrome), 'Accept-Encoding': 'utf-8'}
        task = self.__task
        tag = task["tag"]
        search_url = task["search"]
        result = requests.get(search_url, headers=header)
        content = result.content
        soup = BeautifulSoup(content, "html.parser")
        main_item_div_list = soup.find_all('a', "b-advItem")
        count_all = 0
        count_new = 0
        count_change = 0
        for mainItemDiv in main_item_div_list:
            item_link = mainItemDiv.get('href')
            title_tag = mainItemDiv.find('div', 'b-advItem__title')
            price_tag = mainItemDiv.find('div', 'b-advItem__price')
            item_name = title_tag.text
            item_price = self.__getText(price_tag)
            item_price = re.sub(r"[^0-9]", '', item_price)
            # Нашли цену и url, можем писать в базу
            count_all += 1
            avito_record = dict()
            avito_record['tag'] = tag

            avito_record['link'] = item_link
            avito_record['price'] = item_price
            message = self.__check_record(avito_record)
            if message is not None:
                if 'oldPrice' in message:
                    count_change += 1
                    formatted_message = "{}{}  \n{}  \n💰 {}₽ -> {}  \n🔗[Перейти]({})".format(message['icon'],
                                                                                               message[
                                                                                                   'message'],
                                                                                               item_name,
                                                                                               message[
                                                                                                   'oldPrice'],
                                                                                               avito_record[
                                                                                                   'price'],
                                                                                               avito_record[
                                                                                                   'link'],
                                                                                               )
                    print(formatted_message)
                    self.__tg.send_message(task["tgChannelId"], formatted_message)
                else:
                    count_new += 1
                    formatted_message = "{}{}  \n{}  \n💰 {}₽  \n🔗[Перейти]({})".format(message['icon'],
                                                                                         message['message'],
                                                                                         item_name,
                                                                                         avito_record['price'],
                                                                                         avito_record['link'],
                                                                                         )
                    print(formatted_message)
                    self.__tg.send_message(task["tgChannelId"], formatted_message)

        print("Total: {} new: {} changed: {}".format(count_all, count_new, count_change))

    def __getText(self,parent):
        return ''.join(parent.find_all(text=True, recursive=False)).strip()
