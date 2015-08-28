__author__ = 'onotole'
# -*- coding: utf-8 -*-

import vk_api_auth as vk_auth
import json
import urllib2
from urllib import urlencode
import config
import os
import getpass


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
    return json.loads(urllib2.urlopen(url, params, timeout).read())["response"]


def get_messages(user_id, token):
    return call_api("messages.getDialogs", [("uid", user_id)], token)


# def send_message_to_conversation(user_id, token, text):
#     return call_api("messages.send", [("uid", user_id), ("chat_id", str(conversation_id)), ("message", text)], token)


def send_message(user_id, text, token):
    return call_api("messages.send", [("user_id", str(user_id)), ("message", text)], token)


def create_post_advanced(group_id, text, token):
    if type(group_id) != str and group_id > 0:
        group_id_signed = "-"+str(group_id)
    else:
        group_id_signed = group_id
    return call_api_post("wall.post", [("signed", 1), ("owner_id", group_id_signed), ("message", text)], token)


def create_post(text, label):
    group_id = config.group_for_post_id
    token_inner = token
    result_creating = create_post_advanced(group_id, text, token_inner)
    result_sending = send_message(config.user_for_notification_id, "new post at group " + config.group_for_post_url + " in section " + label, token)
    result = min(result_creating, result_sending)
    return result


token, user_id = vk_auth.auth(config.vk_username, config.vk_password, config.application_id, "messages,wall")



#messages = get_messages(user_id, token)
#send_message_to_conversation(user_id, token, "hello, world!")
#create_post("PEWPEW")
