# coding='utf-8'
# -*- coding: utf-8 -*-

import vk_api_auth as vk_auth
import json
import urllib2
import requests
import schedule
from urllib import urlencode
import config
import datetime
import calendar
import time
import os


def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    result_raw = json.loads(urllib2.urlopen(url).read())
    try:
        result = result_raw["response"]
    except KeyError:
        if result_raw["error"]["error_code"] == 9:
            return True
        print("ERROR")
        print(result_raw)
        raise
    return result


def call_api_post(method, params, token, timeout=5):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s" % (method)
    params = urlencode(params)
    result_raw = json.loads(urllib2.urlopen(url, params, timeout).read())
    try:
        result = result_raw["response"]
    except KeyError:
        if result_raw["error"]["error_code"] == 9:
            return True
        print("ERROR")
        print(result_raw)
        raise
    return result


def get_messages(user_id, token):
    return call_api("messages.getDialogs", [("uid", user_id)], token)


# def send_message_to_conversation(user_id, token, text):
#     return call_api("messages.send", [("uid", user_id), ("chat_id", str(conversation_id)), ("message", text)], token)


def send_message(user_id, text, token_inner=None):
    if not token_inner:
        token_inner = token
    return call_api("messages.send", [("user_id", str(user_id)), ("message", text)], token_inner)


def send_message_to_chat(chat_id, text, token_inner=None):
    if not token_inner:
        token_inner = token
    return call_api("messages.send", [("chat_id", str(chat_id)), ("message", text)], token_inner)


def create_post_advanced(group_id, text, token, delay_hours=0):
    if type(group_id) != str and group_id > 0:
        group_id_signed = "-"+str(group_id)
    else:
        group_id_signed = group_id
    future = datetime.datetime.utcnow() + datetime.timedelta(hours=delay_hours)
    publish_date = calendar.timegm(future.timetuple())
    return call_api_post("wall.post", [("signed", 1), ("owner_id", group_id_signed), ("message", text),
                                       ("publish_date", publish_date)], token)


def create_post(text, label):
    group_id = config.group_for_post_id
    token_inner = token

    #message_for_notify = "After " + str(delay_before_publish) + " hour will be a new post at group " + config.group_for_post_url + " in section " + label
    message_for_notify = u"Новый пост добавлен в очередь через " + str(config.delay_before_publish) +\
                         u" час(ов) в группу " + config.group_for_post_url
    message_for_notify = message_for_notify.encode('utf-8')

    result_creating = create_post_advanced(group_id, text, token_inner, config.delay_before_publish)
    result_sending_to_user = send_message(config.user_for_notification_id, message_for_notify, token)
    result_sending_to_chat = send_message_to_chat(config.chat_for_notification_id, message_for_notify, token)

    result = [result_creating, result_sending_to_user, result_sending_to_chat]
    return result


def upload_picture_to_group(group_id, token):
    if int(group_id) < 0:
        group_id = str(-int(group_id))
    answer = call_api("photos.getWallUploadServer", [("group_id", group_id)], token)
    #answer = call_api("photos.getWallUploadServer", [("user_id", config.user_for_notification_id)], token)
    album_id = answer["aid"]
    upload_url = answer["upload_url"]
    print upload_url
    files = {'file': open('pic2.png', 'rb')}
    r = requests.post(upload_url, files=files)
    print r.json()
    photo_id = json.loads(r.json()["photo"])[0]["photo"]
    photo_hash = r.json()["hash"]
    photo_server = r.json()["server"]

    result_uploading_photo = call_api("photos.saveWallPhoto", [("group_id", config.group_for_post_id), ("photo", photo_id), ("server", photo_server),
                                      ("hash", photo_hash)], token)
    print result_uploading_photo


def postponed_posts(group_id, token):
    postponed_posts_times = []
    if int(group_id) > 0:
        group_id = str(-int(group_id))
    posts_data_raw = call_api("wall.get", [("owner_id", group_id), ("filter", "postponed"), ("count", 50)], token)
    for post_data in posts_data_raw[1:]:
        postponed_posts_times.append(post_data["date"])
    return postponed_posts_times


def convert_today_hour_in_timestamp(hour, minutes=None):
    # 10:00 today -> timestamp
    if not minutes:
        hour, minutes = hour.split(":")
    today = datetime.datetime.now()
    result_time = datetime.datetime(today.year, today.month, today.day, int(hour), int(minutes))
    return time.mktime(result_time.timetuple())


def check_postponed_posts_for_today_advanced(group_id, dict_of_posts, token):
    # dict = {"10:00": "user1", ... }
    posts_to_create = []
    now_timestamp = time.mktime(datetime.datetime.now().timetuple())
    existing_posts = set(postponed_posts(group_id, token))

    for param_for_post in dict_of_posts.items():
        date_for_post = convert_today_hour_in_timestamp(param_for_post[0])
        if date_for_post not in existing_posts and date_for_post > now_timestamp:
            posts_to_create.append(param_for_post)

    return posts_to_create


def check_postponed_posts_for_today():
    group_id = config.group_for_post_id
    dict_of_posts = schedule.posts_time
    token_inner = token
    return check_postponed_posts_for_today_advanced(group_id, dict_of_posts, token_inner)




token, user_id = vk_auth.auth(config.vk_username, config.vk_password, config.application_id, "messages,wall,photos")

#print postponed_posts(config.group_for_post_id, token)
#print(check_postponed_posts_for_today(config.group_for_post_id, schedule.posts_time, token))
#print time.gmtime()

#! upload_picture_to_group(config.group_for_post_id, token)
#send_message_to_chat(config.conversation_for_notification_id, "Hello from bot", token)
#messages = get_messages(user_id, token)
#send_message_to_conversation(user_id, token, "hello, world!")
#create_post("PEWPEW")
