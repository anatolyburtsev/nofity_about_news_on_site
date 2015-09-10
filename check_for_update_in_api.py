__author__ = 'onotole'
import config
import requests
from vk_bot import send_message

req = "https://api.wotblitz.ru/wotb/encyclopedia/info/?application_id=" + \
      config.applicationWGID + "&fields=game_version"

session = requests.Session()
r = session.get(req).json()["data"]["game_version"]
if r != "2.0.0":
    print "API UPDATED!!!"
    send_message(config.user_for_notification_id, "API updated, version: " + r)