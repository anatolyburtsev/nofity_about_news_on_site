#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'onotole'
from bs4 import BeautifulSoup
from bs4 import element
import urllib2
from socket import timeout
from urlparse import urljoin
import sys
import os
import os.path
import time
from vk_bot import create_post
import config

         

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
    return post.attrs["href"]


def get_post_text(url):
    page = load_helper(url)
    post_title_raw = page.find("meta", attrs={'property': 'og:title'})
    post_title = post_title_raw.attrs["content"]

    post_text_raw = page.find("div", attrs={'class': 'b-content'})
    try:
        post_text = post_text_raw.get_text()
    except AttributeError:
        print("ERROR")
        print(post_text_raw)
        raise

    post_pic_raw = page.find("div", attrs={'class':"news-picture"})
    post_pic = post_pic_raw.attrs["style"].split("'")[1]

    post = post_pic + "\n\n" + post_title + "\n\n" + post_text + "\n\n" + url
    return post


def save_last_post(label, post):
    if not os.path.isdir(config.data_dir):
        os.mkdir(config.data_dir)
    with open(os.path.join(config.data_dir, label), 'w') as f:
        f.write(post)


def save_all_last_posts():
    for label in links.keys():
        link = urljoin(ru_prefix, links[label][1])
        post = get_last_post(link)
        save_last_post(label, post)


def get_info_for_platoon_event(url_to_post):
    # обработка "решающего взвода" чуть сложнее
    page = load_helper(url_to_post)

    # получаем ссылку на картинку
    post_pic_raw = page.find("div", attrs={'class': "news-picture"})
    post_pic = post_pic_raw.attrs["style"].split("'")[1]


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
    #print(url_to_post_on_forum)
    post_with_text = page_on_forum.find('div', attrs={'id': post_id})
    title = post_with_text.find('p', attrs={'style': 'text-align:center;'}).get_text()

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

    for p in table_raw.find_all('p', attrs={'style': "background:none;", 'align': 'center'}):
        if i % 5 == 0:
            # номер игрока
            table_text += p.get_text()
            table_text += ". "
        if i % 5 == 1:
            # ник игрока
            username = p.get_text()
            if username in our_clan:
                our_clan_mates += username
                our_clan_mates += '\n'
            table_text += username
            table_text += " - "
        if i % 5 == 2:
            # количество медалей
            table_text += p.get_text()
            table_text += u" медалей\n"
        i += 1

    post_text = post_pic + "\n\n" + title + "\n\n" + u"Поздравляем наших соклановцев:\n" + our_clan_mates + "\n\n" +\
                pre_table_text + "\n" + table_text + "\n\n" + u"Новость на форуме: " + url_to_post_on_forum
    return post_text


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
            # Detected new post
            notify(label, post)
            save_last_post(label, post)


def notify(label, post):
    url = urljoin(config.ru_prefix, post)
    if not "platoon_event" in post:
        post_text = get_post_text(url)
    else:
        post_text = get_info_for_platoon_event(url)
    #print(post_text)
    create_post(post_text.encode('utf-8'), label)
    #print(url)


#print(get_posts_list("http://wotblitz.ru/ru/news/pc-browser/specials"))
#print(get_last_post("http://wotblitz.ru/ru/news/pc-browser/specials"))
#print(get_post_text("http://wotblitz.ru/ru/news/pc-browser/specials/top-destroyers/"))
#print(links["common"][1])
#save_all_last_posts()

check_for_new_posts()
