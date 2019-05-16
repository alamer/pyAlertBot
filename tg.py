# import logging
import os
import urllib.request

import telebot
from telebot import apihelper


class Tg:
    """docstring"""

    def __init__(self, token, proxy=None):
        """Constructor"""
        self._proxy = proxy
        self._token = token
        if proxy is not None:
            apihelper.proxy = {'https': self._proxy}
        self._bot = telebot.TeleBot(self._token)

    def send_message(self, chat, text, method='sendMessage'):
        # logger = telebot.logger
        # telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

        self._bot.send_message(chat, text, parse_mode="markdown")

    def send_message_image(self, chat, url, message, method='sendMessage'):
        filename = os.path.basename(url)
        filename1, file_extension = os.path.splitext(filename)
        f = open(filename, 'wb')
        f.write(urllib.request.urlopen(url).read())
        f.close()
        img = open(filename, 'rb')
        if file_extension == '.jpg' or file_extension == '.jpeg' or file_extension == '.png':
            if len(message) > 200:
                self._bot.send_message(chat, message)
                self._bot.send_photo(chat, img)
            else:
                self._bot.send_photo(chat, img, message)
        if file_extension == '.gif':
            self._bot.send_document(chat, img, message)
        img.close()
        os.remove(filename)


if __name__ == "__main__":
    print("tgmodule")
