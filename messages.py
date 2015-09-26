#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'onotole'
from vk_bot import MessageException, get_schedule, save_schedule, show_schedule, send_message_to_chat, call_api
from vk_bot import token, send_random_picture_to_chat_from_dir
import vk_bot
import config
import logging
import time
admin_chat_id = config.chat_for_notification_id

logging.basicConfig(format=config.logging_format, level=config.logging_level, filename=config.logging_filename)


def analyze_and_get_answer_admin(message_raw):
    start_time = time.time()
    message = message_raw.split(" ")
    if not message[0].startswith(config.bot_name[:-1]):
        message_to_chat = ""

    elif len(message) < 2:
        raise MessageException

    # расписание
    elif len(message) > 4 and message[2] == u'установить'.encode('utf-8') and len(message[3]) > 3 and message[4] and message[5]:
        # бот расписание установить 10:00 Ник рубрика
        if len(message[3].split(':')) != 2:
            message_to_chat = u'Ошибка во времени. Должно быть как-то так 10:00'
        else:
            hours, minutes = message[3].split(':')
            try:
                hours = int(hours)
                minutes = int(minutes)
            except ValueError:
                raise MessageException
            current_schedule = get_schedule()
            chapter = ""
            for i in message[5:]:
                chapter = chapter + i + " "
            current_schedule[message[3]] = [message[4], chapter]
            save_schedule(current_schedule)
            message_to_chat = show_schedule(get_schedule())
    elif len(message) > 2 and u'расписан'.encode('utf-8') in message_raw and u'пока'.encode('utf-8') in message_raw:
        message_to_chat = show_schedule(get_schedule())
    elif len(message) > 2 and message[2].lower() == u'очистить'.encode('utf-8'):
        save_schedule({})
        message_to_chat = u'да, мой повелитель'

    #stupid part
    elif u'ты'.encode('utf-8') in message_raw and u'где'.encode('utf-8') in message_raw:
        message_to_chat = u'Валеры здесь нет!'
    elif u'твое'.encode('utf-8') in message_raw and u'время'.encode('utf-8') in message_raw:
        message_to_chat = u'ПиуПиу'
    elif u'как'.encode('utf-8') in message_raw and (u'дел'.encode('utf-8') in message_raw or u'жиз'.encode('utf-8') in message_raw):
        message_to_chat = u'Ваще огонь'
    elif u'молод'.encode('utf-8') in message_raw or u'умни'.encode('utf-8') in message_raw or \
                    u'огонь'.encode('utf-8') in message_raw:
        message_to_chat = u"I'm sexy and I know it"
    elif u'чо'.encode('utf-8') in message_raw and u'дела'.encode('utf-8') in message_raw:
        message_to_chat = u'извини, хозяин, накосячил'
    elif len(message) > 2 and u'дел'.encode('utf-8') in message_raw and (u'что'.encode('utf-8') in message_raw or
    u'чо'.encode('utf-8') in message_raw):
        message_to_chat = u'На благо группы х*ярю!'
    elif u'разберись'.encode('utf-8') in message_raw:
        message_to_chat = u'ну все, ты попал! Валера, вперед!'

    else:
        raise MessageException
    logging.debug("finish analyze message in sec: " + str(time.time() - start_time))
    return ["text", message_to_chat.encode('utf-8')]


def analyze_and_get_answer(message_raw):
    start_time = time.time()
    message = message_raw.split(" ")
    if not message[0].startswith(config.bot_name[:-1]):
        message_to_chat = ""

    elif len(message) < 2:
        raise MessageException

    elif u'шут'.encode('utf-8') in message_raw or u'еще'.encode('utf-8') in message[1] or u'да'.encode('utf-8') in message[1]:
        message_to_chat = u'еще?'.encode('utf-8')
        return ["picture", message_to_chat]
    elif u'гиф'.encode('utf-8') in message_raw and u'лучши'.encode('utf-8') in message_raw or \
                            u'gif'.encode('utf-8') in message[1] and u'best'.encode('utf-8') in message_raw:
        message_to_chat = u'Вот ваши гифочки:'.encode('utf-8')
        return ["gif_best", message_to_chat]
    elif u'гиф'.encode('utf-8') in message[1] or u'gif'.encode('utf-8') in message[1]:
        message_to_chat = u'Вот ваши гифочки:'.encode('utf-8')
        return ["gif", message_to_chat]
    #stupid part

    elif u'твое'.encode('utf-8') in message_raw and u'время'.encode('utf-8') in message_raw:
        message_to_chat = u'ПиуПиу'
    elif u'как'.encode('utf-8') in message_raw and (u'дел'.encode('utf-8') in message_raw or u'жиз'.encode('utf-8') in message_raw):
        message_to_chat = u'Ваще огонь'
    elif u'молод'.encode('utf-8') in message_raw or u'умни'.encode('utf-8') in message_raw or \
                    u'огонь'.encode('utf-8') in message_raw:
        message_to_chat = u"I'm sexy and I know it"
    elif u'чо'.encode('utf-8') in message_raw and u'дела'.encode('utf-8') in message_raw:
        message_to_chat = u'извини, хозяин, накосячил'
    elif len(message) > 2 and u'дел'.encode('utf-8') in message_raw and (u'что'.encode('utf-8') in message_raw or
    u'чо'.encode('utf-8') in message_raw):
        message_to_chat = u'На благо группы х*ярю!'
    elif u'анекдот'.encode('utf-8') in message_raw and u'18'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_anecdote18()
    elif u'анекдот'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_anecdote()
    elif u'афоризм'.encode('utf-8') in message_raw and u'18'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_aphorism18()
    elif u'афоризм'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_aphorism()
    elif u'цитат'.encode('utf-8') in message_raw and u'18'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_quote18()
    elif u'цитат'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_quote()
    elif u'тост'.encode('utf-8') in message_raw and u'18'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_rouse18()
    elif u'тост'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_rouse()
    elif u'сти'.encode('utf-8') in message_raw and u'18'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_poem18()
    elif u'сти'.encode('utf-8') in message_raw:
        message_to_chat = vk_bot.get_poem()
    elif u'разберись'.encode('utf-8') in message_raw:
        message_to_chat = u'ну все, ты попал! Валера, вперед!'
    elif u'ты'.encode('utf-8') in message_raw and (u'где'.encode('utf-8') in message_raw or u'здесь'.encode('utf-8')):
        message_to_chat = u'Валеры здесь нет!'
    else:
        raise MessageException
    logging.debug("finish analyze message in sec: " + str(time.time() - start_time))
    return ["text", message_to_chat.encode('utf-8')]


#speach part
def get_unread_messages(token, chat_id=config.chat_for_notification_id, ):
    all_messages_list = call_api("messages.get", [("count", "20")], token)
    messages_from_users = []
    messages_from_chats = []
    messages_admins = []
    for message_raw in all_messages_list[1:]:
        if message_raw["read_state"] == 0:
            if "chat_id" in message_raw :
                if message_raw["chat_id"] == chat_id:
                    messages_admins.append(message_raw)
                else:
                    messages_from_chats.append(message_raw)
            else:
                messages_from_users.append(message_raw)

    for messages in [messages_admins, messages_from_chats, messages_from_users]:
        if not config.testing_mode and len(messages) > 0:
            call_api("messages.markAsRead", [("message_ids", messages[0]["mid"])], token)
    return [messages_admins, messages_from_chats, messages_from_users]


def analyze_message(message_raw, token, fromChat=False):
    if fromChat:
        if fromChat == admin_chat_id:
            message_to_chat = analyze_and_get_answer_admin(message_raw["body"].lower().encode('utf-8'))
            if message_to_chat[0] == u"picture":
                return send_random_picture_to_chat_from_dir(message_raw["chat_id"], config.humor_pics_dir, token)
            else:
                return send_message_to_chat(message_raw["chat_id"], message_to_chat[1], token)
        else:
            message_to_chat = analyze_and_get_answer(message_raw["body"].lower().encode('utf-8'))
            if message_to_chat[0] == u"picture":
                return send_random_picture_to_chat_from_dir(message_raw["chat_id"], config.humor_pics_dir, token)
            elif message_to_chat[0] == u"gif":
                return vk_bot.send_random_docs_to_chat_from_hdd(message_raw["chat_id"], token, False)
            elif message_to_chat[0] == u"gif_best":
                return vk_bot.send_random_docs_to_chat_from_hdd(message_raw["chat_id"], token, True)
            else:
                return send_message_to_chat(message_raw["chat_id"], message_to_chat[1], token)
    else:
        message_to_chat = analyze_and_get_answer(message_raw["body"].lower().encode('utf-8'))
        if message_to_chat[0] == u"picture":
            return vk_bot.send_random_picture_to_user_from_dir(message_raw["uid"], config.humor_pics_dir, token)
        elif message_to_chat[0] == u"gif":
            return vk_bot.send_random_docs_to_user_from_hdd(message_raw["uid"], token, False)
        elif message_to_chat[0] == u"gif_best":
            return vk_bot.send_random_docs_to_user_from_hdd(message_raw["uid"], token, True)
        else:
            return vk_bot.send_message_to_user(message_raw["uid"], message_to_chat[1], token)


def check_messages():
    unread_messages = get_unread_messages(token)
    # from admins conversation
    for message in unread_messages[0]:
        try:
            analyze_message(message, token, admin_chat_id)
        except MessageException:
            message_to_chat = u"я могу показать расписание:\n" +\
                              config.bot_name.decode('utf-8') + u" расписание показать \n\n" \
                              u"и установить нового ответственного:\n" +\
                              config.bot_name.decode('utf-8') + u" расписание установить 10:00 Имя Рубрика\n\n"
            message_to_chat = message_to_chat.encode('utf-8')
            send_message_to_chat(message["chat_id"], message_to_chat, token)

    #from chats
    for message in unread_messages[1]:
        try:
            analyze_message(message, token, message["chat_id"])
        except MessageException:
            message_to_chat = u"Я могу рассказать стишок:\n".encode('utf-8') +\
                str(config.bot_name) + u" стих \n".encode('utf-8') + \
                u'или\n'.encode('utf-8') + \
                str(config.bot_name) + u' стих 18+\n'.encode('utf-8') + \
                u" А еще могу рассказать анекдот, анекдот 18+,\n ".encode('utf-8') + \
                u" и даже тост и тост 18+, афоризм и афоризм 18+, цитаты и цитаты 18+\n".encode('utf-8') +\
                u" и показать смешную картинку по запросу:\n".encode('utf-8') +\
                config.bot_name + u" шуточку в студию".encode('utf-8')
            send_message_to_chat(message["chat_id"], message_to_chat, token)

    for message in unread_messages[2]:
        try:
            analyze_message(message, token)
        except MessageException:
            message_to_chat = u"Я могу рассказать стишок:\n".encode('utf-8') +\
                str(config.bot_name) + u" стих \n".encode('utf-8') + \
                u'или\n'.encode('utf-8') + \
                str(config.bot_name) + u' стих 18+\n'.encode('utf-8') + \
                u" А еще могу рассказать анекдот, анекдот 18+,\n ".encode('utf-8') + \
                u" и даже тост и тост 18+, афоризм и афоризм 18+, цитаты и цитаты 18+\n".encode('utf-8') +\
                u" и показать смешную картинку по запросу:\n".encode('utf-8') +\
                config.bot_name + u" шуточку в студию".encode('utf-8')
            vk_bot.send_message_to_user(message["uid"], message_to_chat, token)


