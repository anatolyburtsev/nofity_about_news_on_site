#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'onotole'
from bs4 import BeautifulSoup
import urllib2
from socket import timeout
import sys
import time


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
    post_text = post_text_raw.get_text()

    post = post_title + "\n\n" + post_text
    return post





#print(get_posts_list("http://wotblitz.ru/ru/news/pc-browser/specials"))
#print(get_last_post("http://wotblitz.ru/ru/news/pc-browser/specials"))
print(get_post_text("http://wotblitz.ru/ru/news/pc-browser/specials/top-destroyers/"))