# coding='utf-8'
# -*- coding: utf-8 -*-

import vk_api_auth as vk_auth
import json
import urllib
import urllib2
import requests
import schedule
from urllib import urlencode
import config
import datetime
import logging
import calendar
import time
import config
import os
import signal
import random
from pprint import pprint

logging.basicConfig(format=config.logging_format, level=config.logging_level, filename=config.logging_filename)

class MessageException(Exception):
    def __init__(self, value="Error in message"):
        self.value = value

    def __str__(self):
        return repr(self.value)


class APIErrorException(Exception):
    def __init__(self, value="Error in message"):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TimeoutError(Exception):
    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


def timeout(seconds_before_timeout):
    def decorate(f):
        def handler(signum, frame):
            raise TimeoutError()

        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds_before_timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
            return result
        new_f.func_name = f.func_name
        return new_f
    return decorate


def call_api(method, params, token):
    params_initial = params
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    try:
        result_raw = json.loads(urllib2.urlopen(url).read())
    except urllib2.URLError:
        logging.error('couldnt load site ' + url)
        raise
    if "response" in result_raw.keys():
        result = result_raw["response"]
    elif "error" in result_raw.keys():
        if result_raw["error"]["error_code"] == 9:
            return True
        # Too many requests per second
        elif result_raw["error"]["error_code"] == 6:
            time.sleep(1)
            logging.debug("Too many requests per second")
            return call_api(method, params_initial, token)
        else:
            print(result_raw["error"]["error_msg"])
            logging.warning("error with vk api")
            logging.warning(url)
            logging.warning(result_raw)
            raise APIErrorException
    return result


def call_api_post(method, params, token, timeout=5):
    params_initial = params
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s" % (method)
    params = urlencode(params)
    try:
        result_raw = json.loads(urllib2.urlopen(url, params, timeout).read())
    except urllib2.URLError:
        logging.error('couldnt load site ' + url)
        raise
    try:
        result = result_raw["response"]
    except KeyError:
        print result_raw["error"]["error_msg"]
        if result_raw["error"]["error_code"] == 9:
            return True

        elif result_raw["error"]["error_code"] == 6:
            time.sleep(1)
            logging.debug("Too many requests per second")
            return call_api_post(method, params_initial, token, timeout)

        elif result_raw["error"]["error_code"] == 214:
            logging.debug("post already exist for this time")
            #time.sleep(60)
            return False

        logging.info("error with vk api")
        logging.info(result_raw)
        raise
    return result


def send_message(user_id, text, token_inner=None):
    if not token_inner:
        token_inner = token
    return call_api("messages.send", [("user_id", str(user_id)), ("message", text)], token_inner)


def send_message_to_chat(chat_id, text, token_inner=None):
    if text == "":
        return True
    if not token_inner:
        token_inner = token
    return call_api("messages.send", [("chat_id", str(chat_id)), ("message", text)], token_inner)


def send_picture_to_chat_from_hdd(chat_id, picture_path, token_inner=None):
    chat_id = abs(int(chat_id))
    photo_id = upload_picture_to_chat_from_hdd(picture_path)
    return call_api("messages.send", [("chat_id", str(chat_id)), ("attachment", photo_id)], token_inner)


def send_random_picture_to_chat_from_dir(chat_id, path_to_dir, token_inner=None):
    photo_path = choose_random_humor_from_hdd(config.humor_pics_dir)
    return send_picture_to_chat_from_hdd(chat_id, photo_path, token_inner)


def create_post_advanced(group_id, text, token, pictures_urls=[], delay_hours=0, delay_minutes=0):
    if type(group_id) != str and group_id > 0:
        group_id_signed = "-"+str(group_id)
    else:
        group_id_signed = group_id
    future = datetime.datetime.utcnow()
    publish_date = calendar.timegm(future.timetuple())
    print("publish_date before" + str(publish_date))
    publish_date += delay_hours * 3600 + delay_minutes * 60
    print("publish_date after" + str(publish_date))
    print ("delay_minutes:" + str(delay_minutes))
    attachments = ""
    for pic_url in pictures_urls:
        pic_id = upload_picture_to_group_by_url(group_id, pic_url, token)
        if pic_id:
            attachments += pic_id
            attachments += ","
    attachments = attachments[:-1]

    if config.debug_mode:
        return 0
    else:
        result = call_api_post("wall.post", [("signed", 1),
                                           ("owner_id", group_id_signed),
                                           ("message", text),
                                           ("publish_date", publish_date),
                                           ("attachments", attachments)], token)
        if not result:
            # if post for this time already exist, post after 2 minutes
            result = create_post_advanced(group_id, text, token, pictures_urls, delay_hours, random.randrange(150))
        return result


def create_post(text, label, pictures_urls=[]):
    group_id = config.group_for_post_id
    token_inner = token

    # message_for_notify = u"пост будет через " + str(config.delay_before_publish) +\
    #                      u" час в группе " + config.group_for_post_url +

    result_creating = create_post_advanced(group_id, text, token_inner, pictures_urls, config.delay_before_publish)
    if config.debug_mode:
        post_id = 1
    else:
        post_id = result_creating["post_id"]
    message_for_notify = u"Новый пост: https://vk.com/wall-" + str(config.group_for_post_id) + "_" + \
                         str(post_id) + u". Рубрика " + config.links[label][0]
    message_for_notify = message_for_notify.encode('utf-8')
    if not config.debug_mode:
        result_sending_to_chat = send_message_to_chat(config.chat_for_notification_id, message_for_notify, token)
        result = [result_creating, result_sending_to_chat]
    else:
        print("Message to chat:" + message_for_notify)
        #print("post text: \n" + text)
        result = 0
    return result


def save_picture_by_url_to_hdd(picture_url):
    #logging.debug("saving picture by url: " + picture_url)
    picture_filename = picture_url.split('/')[-1]
    if not os.path.isdir(config.pic_dir):
        os.mkdir(config.pic_dir)
    picture_path = os.path.join(config.pic_dir, picture_filename)
    urllib.urlretrieve(picture_url, picture_path)
    return picture_path


def upload_picture_to_group_by_url(group_id, picture_url, token):
    picture_path = save_picture_by_url_to_hdd(picture_url)
    return upload_picture_to_group_from_hdd(group_id, picture_path, token)


def upload_picture_to_group_from_hdd(group_id, picture_path, token, force=False):
    # picture_description = "blah"
    statinfo = os.stat(picture_path)
    if not force and statinfo.st_size < config.small_picture_limit:
        return False
    if int(group_id) < 0:
        group_id = str(-int(group_id))
    answer = call_api("photos.getWallUploadServer", [("group_id", group_id)], token)

    album_id = answer["aid"]
    upload_url = answer["upload_url"]
    files = {'file': open(picture_path, 'rb')}
    r = requests.post(upload_url, files=files)

    photo_id = r.json()["photo"]
    photo_hash = r.json()["hash"]
    photo_server = r.json()["server"]
    result_uploading_photo = call_api("photos.saveWallPhoto", [("group_id", config.group_for_post_id),
                                                               ("photo", photo_id),
                                                               ("server", photo_server),
                                                               ("hash", photo_hash)], token)
    # print(result_uploading_photo)
    # call_api("photos.edit", [("owner_id", -int(group_id)),
    #                          ("photo_id", result_uploading_photo[0]["pid"]),
    #                          ("caption", picture_description)], token)
    return result_uploading_photo[0]["id"]


def upload_picture_to_chat_from_hdd(picture_path):
    try:
        picture_path = picture_path.encode('utf-8')
    except UnicodeDecodeError:
        pass
    # picture_description = "blah"
    answer = call_api("photos.getMessagesUploadServer", [], token)
    album_id = answer["aid"]
    upload_url = answer["upload_url"]
    files = {'file': open(picture_path, 'rb')}
    r = requests.post(upload_url, files=files)

    photo_id = r.json()["photo"]
    photo_hash = r.json()["hash"]
    photo_server = r.json()["server"]

    result_uploading_photo = call_api("photos.saveMessagesPhoto", [("photo", photo_id),
                                                               ("server", photo_server),
                                                               ("hash", photo_hash)], token)
    return result_uploading_photo[0]["id"]


def choose_random_humor_from_hdd(path_to_dir):
    files = os.listdir(path_to_dir)
    return os.path.join(path_to_dir, files[random.randrange(len(files))])


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
        for delay_before_remind in config.time_before_remind:
            # time has come or not?
            if abs(date_for_post - (now_timestamp + delay_before_remind*60)) < 30:
                if date_for_post not in existing_posts and date_for_post > now_timestamp:
                    posts_to_create.append(param_for_post)
    return posts_to_create


def check_postponed_posts_for_today():
    group_id = config.group_for_post_id
    dict_of_posts = get_schedule()
    token_inner = token
    missing_posts = check_postponed_posts_for_today_advanced(group_id, dict_of_posts, token_inner)
    return missing_posts


def show_schedule(schedule_dict):
    # {"10:00" : [ник, рубрика]}
    times_list = sorted(schedule_dict.keys())
    output_message = u"Текущее расписание: \n"
    #for times, param in schedule_dict.items():
    for times in times_list:
        param = schedule_dict[times]
        output_message = output_message + times + u" - товарищ: " + param[0] + \
                         u", рубрика: " + unicode(param[1]) + "\n"
    #output_message = output_message.encode('utf-8')
    return output_message


def get_schedule(filename="schedule.json"):
    try:
        with open(filename) as data_file:
            data = json.load(data_file)
    except IOError:
        return {}
    return data


def save_schedule(schedule_dict, filename="schedule.json"):
    assert type(schedule_dict) == dict
    with open(filename, 'w') as outfile:
        json.dump(schedule_dict, outfile)


@timeout(5*60)
def get_token(username, password, application_id, scopes):
    try:
        with open(config.token_filename, 'r') as f:
            user_id = f.readline()
            token = f.readline()
            call_api("messages.get", [("count", 1)], token)
    except: #IOError or KeyError:
        logging.info("token for vk is outdated, start getting new")
        token, user_id = vk_auth.auth(username, password, application_id, scopes)
        logging.info("got new token for vk")
        f = open(config.token_filename, 'w')
        f.write(user_id+'\n')
        f.write(token)
        f.close()
    return [user_id, token]


#logging.debug("Start checking token for vk")
start_time = time.time()

user_id, token = get_token(config.vk_username, config.vk_password, config.application_id, config.scopes)

elapsed = time.time() - start_time
logging.debug("Finish checking token for vk in " + str(elapsed) + " seconds")

#upload_picture_to_group_by_url(config.group_for_post_id, "http://static-wbp-ru.gcdn.co/dcont/1.10/fb/image/relief.jpg", token)
#print postponed_posts(config.group_for_post_id, token)
#print(check_postponed_posts_for_today(config.group_for_post_id, schedule.posts_time, token))
#print time.gmtime()

#upload_picture_to_group(config.group_for_post_id, token)
#send_message_to_chat(config.conversation_for_notification_id, "Hello from bot", token)
#messages = get_messages(user_id, token)
#send_message_to_conversation(user_id, token, "hello, world!")
#create_post("PEWPEW")

