# -*- coding: utf-8 -*-
# __author__ = 'onotole'

import config
import vk_bot

if __name__ == "__main__":
    missed_posts_time = vk_bot.check_postponed_posts_for_whole_day(config.group_for_post_id,
                                                                   vk_bot.get_schedule(), vk_bot.token)
    if missed_posts_time:
        message = u'Товарищи! на сегодня отсутствуют несколько постов:\n\n'
        schedule = vk_bot.get_schedule()
        for post_time in missed_posts_time:
            message += post_time + u" - товарищ: " + schedule[post_time][0].title() + u", рубрика: " + \
                       schedule[post_time][1] + "\n"
        message += u'\nСделайте, пожалуйста, на благо группы'
        message = message.encode('utf-8')
        vk_bot.send_message_to_chat(config.chat_for_notification_id, message, vk_bot.token)