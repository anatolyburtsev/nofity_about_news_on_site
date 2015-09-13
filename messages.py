#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'onotole'
from vk_bot import MessageException, get_schedule, save_schedule, show_schedule, send_message_to_chat, call_api
from vk_bot import token, send_random_picture_to_chat_from_dir
import vk_bot
import config
import logging
import time

logging.basicConfig(format=config.logging_format, level=config.logging_level, filename=config.logging_filename)


def analyze_and_get_answer(message_raw):
    #logging.debug("start analyze message")
    start_time = time.time()
    message = message_raw.split(" ")
    # for i in range(len(message)):
    #     message[i] = message[i].encode('utf-8')
    # if config.bot_name not in message[0] and (config.bot_name in message_raw or u'бот' in message_raw):
    #     message_to_chat = u'Я - Валера'
    if not message[0].startswith(config.bot_name[:-1]):
        message_to_chat = ""

    elif len(message) < 2:
        raise MessageException

    # расписание
    elif len(message) > 4 and message[2] == u'установить'.encode('utf-8') and len(message[3]) > 3 and message[4] and message[5]:
        # бот расписание установить 10:00 Ник рубрика
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

    elif u'шут'.encode('utf-8') in message_raw or u'еще'.encode('utf-8') in message[1] or u'да'.encode('utf-8') in message[1]:
        message_to_chat = u'еще?'.encode('utf-8')
        return ["picture", message_to_chat]

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

    elif u'разберись'.encode('utf-8'):
        message_to_chat = u'ну все, ты попал! Валера, вперед!'


    else:
        raise MessageException
    logging.debug("finish analyze message in sec: " + str(time.time() - start_time))
    return ["text", message_to_chat.encode('utf-8')]


#speach part
def get_unread_messages(token, chat_id=config.chat_for_notification_id, ):
    all_messages_list = call_api("messages.get", [("count", "20")], token)
    messages = []
    for message_raw in all_messages_list[1:]:
        if "chat_id" in message_raw and message_raw["chat_id"] == chat_id and message_raw["read_state"] == 0:
            messages.append(message_raw)

    if not config.testing_mode and len(messages) > 0:
         call_api("messages.markAsRead", [("message_ids", messages[0]["mid"])], token)
    return messages


def analyze_message(message_raw, token):

    message_to_chat = analyze_and_get_answer(message_raw["body"].lower().encode('utf-8'))
    if message_to_chat[0] == u"picture":
        send_message_to_chat(message_raw["chat_id"], message_to_chat[1], token)
        return send_random_picture_to_chat_from_dir(message_raw["chat_id"], config.humor_pics_dir, token)
    else:
        return send_message_to_chat(message_raw["chat_id"], message_to_chat[1], token)


def check_messages():
    for message in get_unread_messages(token):
        try:
            analyze_message(message, token)
        except MessageException:
            message_to_chat = u"я могу показать расписание:\n" +\
                              config.bot_name.decode('utf-8') + u" расписание показать \n\n" \
                              u"и установить нового ответственного:\n" +\
                              config.bot_name.decode('utf-8') + u" расписание установить 10:00 Имя Рубрика\n\n" + \
                u" могу показать анекдот, анекдот 18+,\n " + \
                u" а еще тост и тост 18+, афоризм и афоризм 18+, цитаты и цитаты 18+\n"
            if "chat_id" in message:
                message_to_chat = message_to_chat.encode('utf-8')
                send_message_to_chat(message["chat_id"], message_to_chat, token)
            else:
                #message from people, not from chat
                pass
