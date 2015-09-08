# -*- coding: utf-8 -*-
__author__ = 'onotole'

from vk_bot import check_postponed_posts_for_today, send_message_to_chat
import random
import config


phrases = [u", нам нужен твой пост на ", u", от твоего поста зависит будущее, не забудь: ",
           u", будь добр, удели время для постика на ", u", просто сделай пост на ", u", понимаю твою занятость, но пост нужен. ",
           u", ты ведь не забыл про ", u", пост сам себя не поставит: ", u", just do it ", u", be a good boy, create a post for time: "]


for missing_post in check_postponed_posts_for_today():
    phrase = phrases[random.randrange(len(phrases))]
    missing_post_time = missing_post[0]
    missing_post_info = missing_post[1]
    missing_post_info[0].encode('utf-8')
    missing_post_info[1].encode('utf-8')
    message = missing_post_info[0] + phrase \
              + missing_post_time \
              + u' Рубрика: ' \
              + missing_post_info[1]
    send_message_to_chat(config.chat_for_notification_id, message.encode('utf-8'))
