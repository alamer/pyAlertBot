import records
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from tg import send_message


class Avito:
    """docstring"""


    def __init__(self, task):
        """Constructor"""
        self.__task = task  # protected
        # Инициализируем базу
        self.__db = self.__prepare_db(task["database"])

    def __prepare_db(self, link):
        db = records.Database(link)
        conn = db.get_connection()
        with conn:
            conn.query(
                'Create table if not exists AVITO (tag VARCHAR(255),id VARCHAR(255),link VARCHAR(255),price VARCHAR(20))')
        return db

    def __check_record(self, avito_record):
        conn = self.__db.get_connection()
        with conn:
            rows = conn.query(
                "select price from AVITO where tag='{}' and id='{}'".format(avito_record['tag'], avito_record['id']),
                fetchall=True)
            if len(rows) == 0:
                # new item
                conn.query("insert into AVITO (tag,id,link,price) values('{}','{}','{}','{}')"
                           .format(avito_record['tag'], avito_record['id'], avito_record['link'],
                                   avito_record['price']))
                res = {'message': "New", 'icon': '✅'}
            elif int(rows[0]['price']) > int(avito_record['price']):
                # item changed, price down
                conn.query("update AVITO set price='{}' where tag='{}' and id='{}'".format(avito_record['price'],
                                                                                           avito_record['tag'],
                                                                                           avito_record['id']))
                res = {'message': "Price down", 'icon': '👍', 'oldPrice': rows[0]['price']}
            elif int(rows[0]['price']) < int(avito_record['price']):
                # item changed, price up
                conn.query("update AVITO set price='{}' where tag='{}' and id='{}'".format(avito_record['price'],
                                                                                           avito_record['tag'],
                                                                                           avito_record['id']))
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
        base_url = "https://www.avito.ru"
        search_url = task["search"]
        result = requests.get(base_url + search_url, headers=header)
        content = result.content
        soup = BeautifulSoup(content, "html.parser")
        main_item_div_list = soup.find_all('div', "item")
        count_all = 0
        count_new = 0
        count_change = 0
        for mainItemDiv in main_item_div_list:
            item_id = mainItemDiv['id']
            href_tag = mainItemDiv.find('a', 'item-description-title-link')
            if href_tag is not None:
                price_tag = mainItemDiv.find('span', 'price')
                if price_tag is not None:
                    item_name = href_tag.get('title')
                    item_price = price_tag.get('content')
                    # Нашли цену и url, можем писать в базу
                    count_all += 1
                    avito_record = dict()
                    avito_record['tag'] = tag
                    avito_record['id'] = item_id
                    item_link = base_url + href_tag.get('href')
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
                            send_message(task["tgBotKey"], task["tgChannelId"], formatted_message)
                        else:
                            count_new += 1
                            formatted_message = "{}{}  \n{}  \n💰 {}₽  \n🔗[Перейти]({})".format(message['icon'],
                                                                                                 message['message'],
                                                                                                 item_name,
                                                                                                 avito_record['price'],
                                                                                                 avito_record['link'],
                                                                                                 )
                            print(formatted_message)
                            send_message(task["tgBotKey"], task["tgChannelId"], formatted_message)
            else:
                print("Empty link for {}".format(item_id))

        print("Total: {} new: {} changed: {}".format(count_all, count_new, count_change))
