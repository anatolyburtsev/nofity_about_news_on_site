#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'onotole'
from bs4 import BeautifulSoup
from bs4 import element
import urllib2
from socket import timeout
from urlparse import urljoin
import sys
import re
import os
import os.path
import time
from vk_bot import create_post
import config
import logging

logging.basicConfig(format=config.logging_format, level=config.logging_level, filename=config.logging_filename)


class WebSiteUnavailableException(Exception):
    def __init__(self, value="problem with wotblitz.ru"):
        self.value = value

    def __str__(self):
        return repr(self.value)


def load_helper(uri):
    if type(uri) != str:
        return uri
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    try:
        thing = opener.open(uri, None, 10)
        soup = BeautifulSoup(thing.read(), "lxml")
        if not (soup is None):
            return soup
        else:
            print "soup is None"
            load_helper(uri)
    except (timeout, urllib2.HTTPError, urllib2.URLError) as error:
        sys.stdout.write("{} encountered, hold on, bro".format(error))
        sys.stdout.flush()
        time.sleep(30)
        load_helper(uri)


def get_posts_list(url):
    posts_list = []
    page = load_helper(url)
    posts = page.find_all("a", attrs={'class': 'news-list_link'})
    for post in posts:
        posts_list.append(post.attrs["href"])
    return posts_list


def get_last_post(url):
    page = load_helper(url)
    post = page.find("a", attrs={'class': 'news-list_link'})
    if not post:
        raise WebSiteUnavailableException
    return post.attrs["href"]


def get_post_text(url):
    page = load_helper(url)
    post_title_raw = page.find("meta", attrs={'property': 'og:title'})
    post_title = post_title_raw.attrs["content"].upper()
    post_text_raw = page.find("div", attrs={'class': 'b-content'})
    post_text_raw = str(post_text_raw).replace("<li>", config.li_replaces).replace("</li>", "")

    post_text_raw = post_text_raw.replace('<img alt="" dir="false" height="22" src="http://static-wbp-ru.gcdn.co/dcont/1.10/fb/image/x3.png" style="vertical-align: middle;" width="22"/>', "X3: ")
    post_text_raw = post_text_raw.replace('<img alt="" dir="false" height="22" src="http://static-wbp-ru.gcdn.co/dcont/1.10/fb/image/x5.png" style="vertical-align: middle;" width="22"/>', "X5: ")
    post_text_raw = post_text_raw.replace('<img alt="" dir="false" height="25" src="http://static-wbp-ru.gcdn.co/dcont/1.8/fb/image/tank_discount.png" style="vertical-align: middle;" width="25"/>', "SALE:")
    post_text_raw = BeautifulSoup(post_text_raw, 'lxml')
    pictures_urls = []
    for i in post_text_raw.find_all("img"):

        url_to_pic = i.attrs["src"]
        if "static-wbp" in url_to_pic:
            if "http" not in url_to_pic:
                url_to_pic = urljoin("http:", url_to_pic)
            pictures_urls.append(url_to_pic)
    try:
        post_text = post_text_raw.get_text()
    except AttributeError:
        logging.error("ERROR")
        logging.error(post_text_raw)
        raise

    post_pic_raw = page.find("div", attrs={'class': "news-picture"})
    try:
        post_pic = post_pic_raw.attrs["style"].split("'")[1]
    except AttributeError:
        post_pic = ""
    pictures_urls.append(post_pic)

    post = post_title + "\n\n" + post_text + "\n\n" + url
    return [post, pictures_urls]


def save_last_post(label, post):
    if not os.path.isdir(config.data_dir):
        os.mkdir(config.data_dir)
    with open(os.path.join(config.data_dir, label), 'w') as f:
        f.write(post)


def save_all_last_posts():
    for label in config.links.keys():
        link = urljoin(config.ru_prefix, config.links[label][1])
        post = get_last_post(link)
        save_last_post(label, post)


def get_info_for_platoon_event(url_to_post):
    # обработка "решающего взвода" чуть сложнее
    page = load_helper(url_to_post)

    # получаем ссылку на картинку
    post_pic_raw = page.find("div", attrs={'class': "news-picture"})
    post_pic = [post_pic_raw.attrs["style"].split("'")[1]]

    urls = page.find_all("a", attrs={'target': '_blank'})
    for url_from_post in urls:
        if "topic" in url_from_post.attrs["href"]:
            url_to_post_on_forum = url_from_post.attrs["href"]
            break

    #получение title
    post_id = url_to_post_on_forum.split('#')[-1]
    # entry453689 -> post_id_453689
    post_id = "post_id_"+post_id[5:]
    page_on_forum = load_helper(url_to_post_on_forum)
    print(url_to_post_on_forum)
    post_with_text = page_on_forum.find('div', attrs={'id': post_id})
    title = post_with_text.find('p', attrs={'style': re.compile('text-align:center;')}).get_text()

    pre_table_text = ""
    p_or_table = post_with_text.find_all(['p', 'table'])
    for tag in p_or_table:
        if tag.name == 'table':
            break
        if len(tag.attrs) == 0:
            pre_table_text += tag.get_text()
            pre_table_text += "\n"

    table_raw = post_with_text.find('table')
    table_text = ""
    i = 0
    our_clan_mates = ""
    our_clan = load_clans_user()

    print "TABLE_RAW:"
    print table_raw
    for p in table_raw.find_all('td', attrs={'style': re.compile("background:*none;")}):
        print p
        # if i % 5 == 0:
        #     # номер игрока
        #     table_text += p.get_text()
        #     table_text += ". "
        if i % 5 == 0:
            # ник игрока
            username = p.get_text()
            if username in our_clan:
                our_clan_mates += username
                our_clan_mates += '\n'
            table_text += username
            table_text += " - "
        if i % 5 == 1:
            # количество медалей
            table_text += p.get_text()
            table_text += u" медалей\n"
        i += 1
        print table_text
        print "END!!111111"


    post_text = title + "\n\n" + u"Поздравляем наших соклановцев:\n" + our_clan_mates + "\n\n" +\
                pre_table_text + "\n" + table_text + "\n\n" + u"Новость на форуме: " + url_to_post_on_forum
    return [post_text, post_pic]


def load_clans_user():
    # -> set
    clan = set()
    #TODO check username in API
    line = "blah"
    with open("clan_list.txt", "r") as f:
        while line:
            line = f.readline()[:-1]
            if len(line) > 2:
                clan.add(line)
    return clan


def check_for_new_posts():
    for label in config.links.keys():
        link = urljoin(config.ru_prefix, config.links[label][1])
        post = get_last_post(link)
        try:
            f = open(os.path.join(config.data_dir, label), "r")
            saved_post = f.readline()
            f.close()
        except IOError:
            saved_post = ""
        if post != saved_post:
            logging.info("new post for vk, url=" + post)
            # Detected new post
            notify(label, post)
            if not config.debug_mode:
                save_last_post(label, post)
            #return True


def notify(label, post):
    url = urljoin(config.ru_prefix, post)
    if "platoon_event" not in post:
        post_text, pictures_urls = get_post_text(url)
    else:
        post_text, pictures_urls = get_post_text(url)#get_info_for_platoon_event(url)
    #print(post_text)
    assert type(pictures_urls) == list
    create_post(post_text.encode('utf-8'), label, pictures_urls)
    #print(url)


#print(get_posts_list("http://wotblitz.ru/ru/news/pc-browser/specials"))
#print(get_last_post("http://wotblitz.ru/ru/news/pc-browser/specials"))
#print(get_post_text("http://wotblitz.ru/ru/news/pc-browser/specials/top-destroyers/"))
#print(links["common"][1])
#save_all_last_posts()
if __name__ == "__main__":
    logging.debug("Start")
    start_time = time.time()
    try:
        check_for_new_posts()
    except WebSiteUnavailableException:
        logging.debug("wotblitz site unavailable")
    finally:
        elapsed = time.time() - start_time
        logging.debug("Finish in " + str(elapsed) + " seconds")
