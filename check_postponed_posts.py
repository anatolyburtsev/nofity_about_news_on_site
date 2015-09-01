# -*- coding: utf-8 -*-
__author__ = 'onotole'

from vk_bot import check_postponed_posts_for_today, send_message_to_chat
import random
import config


phrases = [", нам нужен твой пост на ", ", от твоего поста зависит будущее, не забудь: ",
           ", будь добр, удели время для постика на ", ", просто сделай пост на ", ", понимаю твою занятость, но пост нужен. ",
           ", ты ведь не забыл про ", ", пост сам себя не поставит: ", ", just do it ", ", be a good boy, create a post for time: "]


for missing_post in check_postponed_posts_for_today():
    message = missing_post[1] + phrases[random.randrange(len(phrases))] + missing_post[0]
    send_message_to_chat(config.chat_for_notification_id, message)
