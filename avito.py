import records
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from tg import send_message


def prepare_db(link):
    db = records.Database(link)
    conn = db.get_connection()
    with conn:
        conn.query(
            'Create table if not exists AVITO (tag VARCHAR(255),id VARCHAR(255),link VARCHAR(255),price VARCHAR(20))')
    return db


def check_record(db, avito_record):
    conn = db.get_connection()
    with conn:
        rows = conn.query(
            "select price from AVITO where tag='{}' and id='{}'".format(avito_record['tag'], avito_record['id']),
            fetchall=True)
        if len(rows) == 0:
            # new item
            conn.query("insert into AVITO (tag,id,link,price) values('{}','{}','{}','{}')"
                       .format(avito_record['tag'], avito_record['id'], avito_record['link'], avito_record['price']))
            res = {'message': "New", 'icon': '✅'}
        elif int(rows[0]['price']) > int(avito_record['price']):
            # item changed, price down
            res = {'message': "Price down", 'icon': '👍'}
        elif int(rows[0]['price']) < int(avito_record['price']):
            # item changed, price up
            res = {'message': "Price up", 'icon': '👎'}
        else:
            # price not changed
            res = None
    return res


def grab(task):
    ua = UserAgent()
    print(ua.chrome)
    header = {'User-Agent': str(ua.chrome), 'Accept-Encoding': 'utf-8'}
    print(header)
    db = prepare_db(task["database"])
    tag = task["tag"]
    base_url = "https://www.avito.ru"
    search_url = task["search"]
    result = requests.get(base_url + search_url, headers=header)
    content = result.content
    soup = BeautifulSoup(content, "html.parser")
    main_item_div_list = soup.find_all('div', "item")
    for mainItemDiv in main_item_div_list:
        item_id = mainItemDiv['id']
        href_tag = mainItemDiv.find('a', 'item-description-title-link')
        if href_tag is not None:
            item_link = href_tag.get('href')
            price_tag = mainItemDiv.find('span', 'price')
            if price_tag is not None:
                item_price = price_tag.get('content')
                # Нашли цену и url, можем писать в базу
                avito_record = dict()
                avito_record['tag'] = tag
                avito_record['id'] = item_id
                avito_record['link'] = base_url + item_link
                avito_record['price'] = item_price
                print(
                    "ID: {} link: {} price: {}".format(avito_record['id'], avito_record['link'], avito_record['price']))
                message = check_record(db, avito_record)
                if message is not None:
                    formatted_message = "{} {} price: {}".format(message['icon'], avito_record['link'],
                                                                 avito_record['price'])
                    # print(formated_message)
                    send_message(task["tgBotKey"], task["tgChannelId"], formatted_message)
        else:
            print("Empty link for {}".format(item_id))
