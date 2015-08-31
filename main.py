#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'onotole'
from bs4 import BeautifulSoup
import urllib2
from socket import timeout
from urlparse import urljoin
import sys
import os
import os.path
import time
from vk_bot import create_post


#consts
data_dir = "data"
ru_prefix = "http://wotblitz.ru/ru"
links = {"common": ["Новости", "news/pc-browser/common"],
         "maintenance": ["Технические", "news/pc-browser/maintenance"],
         "media": ["Медиа", "news/pc-browser/media"],
         "community": ["От игроков", "news/pc-browser/community"],
         "guide": ["Руководства", "news/pc-browser/guide"],
         "specials": ["Акции", "news/pc-browser/specials"]
         }
         

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
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    with open(os.path.join(data_dir, label), 'w') as f:
        f.write(post)


def save_all_last_posts():
    for label in links.keys():
        link = urljoin(ru_prefix, links[label][1])
        post = get_last_post(link)
        save_last_post(label, post)


def check_for_new_posts():
    for label in links.keys():
        link = urljoin(ru_prefix, links[label][1])
        post = get_last_post(link)
        try:
            f = open(os.path.join(data_dir, label), "r")
            saved_post = f.readline()
            f.close()
        except IOError:
            saved_post = ""
        if post != saved_post:
            # Detected new post
            notify(label, post)
            save_last_post(label, post)


def notify(label, post):
    url = urljoin(ru_prefix, post)
    post_text = get_post_text(url)
    #print(label)
    #print(post_text)
    create_post(post_text.encode('utf-8'), label)
    #print(url)


#print(get_posts_list("http://wotblitz.ru/ru/news/pc-browser/specials"))
#print(get_last_post("http://wotblitz.ru/ru/news/pc-browser/specials"))
#print(get_post_text("http://wotblitz.ru/ru/news/pc-browser/specials/top-destroyers/"))
#print(links["common"][1])
#save_all_last_posts()

check_for_new_posts()
