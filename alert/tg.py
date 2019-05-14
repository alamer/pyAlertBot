#import logging
import os
import urllib.request

import telebot


def send_message(token, chat, text, method='sendMessage'):
    #logger = telebot.logger
    #telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.
    bot = telebot.TeleBot(token)
    bot.send_message(chat, text)


def send_message_image(token, chat, url, message, method='sendMessage'):
    bot = telebot.TeleBot(token)
    filename = os.path.basename(url)
    filename1, file_extension = os.path.splitext(filename)
    f = open(filename, 'wb')
    f.write(urllib.request.urlopen(url).read())
    f.close()
    img = open(filename, 'rb')
    if file_extension == '.jpg' or file_extension == '.jpeg' or file_extension == '.png':
        if len(message) > 200:
            bot.send_message(chat, message)
            bot.send_photo(chat, img)
        else:
            bot.send_photo(chat, img, message)
    if file_extension == '.gif':
        bot.send_document(chat, img, message)
    img.close()
    os.remove(filename)


if __name__ == "__main__":
    print("tgmodule")
