import records
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from alert.tg import send_message


def prepare_db(link):
    db = records.Database(link)
    conn=db.get_connection()
    with conn:
        conn.query('Create table if not exists AVITO (tag VARCHAR(255),id VARCHAR(255),link VARCHAR(255),price VARCHAR(20))')
    return db


def check_record(db, avito_record):
    conn = db.get_connection()
    with conn:
        rows = conn.query(
            "select id from AVITO where tag='{}' and id='{}' and price='{}'".format(avito_record['tag'], avito_record['id'],
                                                                                    avito_record['price']), fetchall=True)
        if len(rows) == 0:
            # Пишем в базу
            conn.query("insert into AVITO (tag,id,link,price) values('{}','{}','{}','{}')"
                     .format(avito_record['tag'], avito_record['id'], avito_record['link'], avito_record['price']))
    return len(rows)


def grab(task):
    ua = UserAgent()
    print(ua.chrome)
    header = {'User-Agent': str(ua.chrome), 'Accept-Encoding': 'utf-8'}
    print(header)
    db = prepare_db(task["database"])
    tag = task["tag"]
    baseUrl = "https://www.avito.ru"
    searchUrl = task["search"]
    result = requests.get(baseUrl + searchUrl, headers=header)
    content = result.content
    soup = BeautifulSoup(content, "html.parser")
    itemTable = soup.find('div', 'catalog-list')
    mainItemDivList = soup.find_all('div', "item")
    for mainItemDiv in mainItemDivList:
        itemId = mainItemDiv['id']
        hrefTag = mainItemDiv.find('a', 'item-description-title-link')
        if hrefTag != None:
            itemLink = hrefTag.get('href')
            priceTag = mainItemDiv.find('span', 'price')
            if priceTag != None:
                itemPrice = priceTag.get('content')
                # Нашли цену и url, можем писать в базу
                avitoRecord = dict()
                avitoRecord['tag'] = tag
                avitoRecord['id'] = itemId
                avitoRecord['link'] = baseUrl + itemLink
                avitoRecord['price'] = itemPrice
                print("ID: {} link: {} price: {}".format(avitoRecord['id'], avitoRecord['link'], avitoRecord['price']))
                if check_record(db, avitoRecord) == 0:
                    print("new record")
                    message = "{} price: {}".format(baseUrl + itemLink, itemPrice)
                    send_message(task["tgBotKey"], task["tgChannelId"], message)
        else:
            print("Empty link for {}".format(itemId))
