__author__ = 'onotole'
from vk_bot import check_messages
import logging
import config

logging.basicConfig(format=config.logging_format, level=config.logging_level, filename="reading_messages.log")


logging.debug("Start checking messages")
check_messages()
logging.debug("Finish checking messages")
