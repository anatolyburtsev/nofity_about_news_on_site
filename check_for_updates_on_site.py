# -*- coding: utf-8 -*-
__author__ = 'onotole'

from main import load_helper
import vk_bot
import requests
import config

url_for_watching = u'http://riseofcontinents.com/'

r = requests.get(url_for_watching)

if len(r.text) != 71502:
    message_to_chat = u"Алярм! сайт ожил. http://riseofcontinents.com/".encode('utf-8')
    vk_bot.send_message_to_chat(config.chat_for_notification_id, message_to_chat)

