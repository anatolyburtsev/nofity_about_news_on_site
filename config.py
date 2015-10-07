#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from local_config import *

# local_config contain just
# debug_mode = False
# testing_mode = False
assert testing_mode >= debug_mode

# vk
vk_username = "79269900495"
vk_password = "sT2ANSbsMGnReQ3r2SvWaeGMtyz9QJ2qt"

application_id = "4434173"

# mine
user_for_notification_id = "2249344"
user_for_gif = "99605247"

email_from_addr = "bot_vk_valera@mail.ru"
email_from_password = "iWYIOG53bsW3Nl9pcmcbKh3IZSwg4X"
# email_from_addr = "onotolemobile@gmail.com"
# email_from_password = "CRonT3517@@"
email_to_addr = "XGaminG_gif@mail.ru"
email_limit = 30*1024*1024 #30Mb

# XGAMING_conversation_id = 257742
if testing_mode:
    chat_for_notification_id = 1
    group_for_post_id = 87512171
    group_for_post_url = "https://vk.com/wotblitzstat"
else:
    # XGaminG_group_id = 79514596
    chat_for_notification_id = 2
    group_for_post_id = 79514596
    group_for_post_url = "https://vk.com/x_community"

# картинки меньшего размера в байтах не будут загружаться в группу
small_picture_limit = 50000
secs_in_day = 24*60*60

delay_before_publish = 1
# за сколько времени напоминать
time_before_remind = [120, 30]

scopes = "messages,wall,photos,docs,groups"
li_replaces = "*** "


# wg
applicationWGID = "77636487a299e95a72583de66dba7a63"
#server
#applicationWGID="77c7c785ff539689b53b8757553c852a"
ru_prefix = "http://wotblitz.ru/ru"
links = {"common": ["Новости".decode('utf-8'), "news/pc-browser/common"],
         "maintenance": ["Технические".decode('utf-8'), "news/pc-browser/maintenance"],
         #"media": ["Медиа".decode('utf-8'), "news/pc-browser/media"],
         #"community": ["От игроков".decode('utf-8'), "news/pc-browser/community"],
         "guide": ["Руководства".decode('utf-8'), "news/pc-browser/guide"],
         "specials": ["Акции".decode('utf-8'), "news/pc-browser/specials"]
         }


# System
bot_name = u'валера'.encode('utf-8')
data_dir = "data"
pic_dir = "pictures"
memes_dir = "memes"

token_filename = ".token"
logging_format = u'%(filename)s[line:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
logging_level = logging.DEBUG
logging_filename = u"notifier.log"

