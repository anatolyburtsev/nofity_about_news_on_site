# -*- coding: utf-8 -*-
__author__ = 'onotole'


import vk_bot
import config

vk_group_url = "https://vk.com/wotblitz"
token = vk_bot.token

if __name__ == "__main__":
    likes = 0
    reposts = 0
    comments = 0

    likes_for_yest, reposts_for_yest, comments_for_yest = vk_bot.get_all_posts_from_group_by_url("https://vk.com/x_community",
                                             vk_bot.processing_post_count_likes_and_repost,
                                             [likes, reposts, comments],
                                             vk_bot.processing_post_stop_on_yesterdays_post,
                                             token)

    text = "Товарищи! Хорошо вчера поработали: " + str(likes_for_yest) + " лайков, " + str(comments_for_yest) + \
           " комментов и " + str(reposts_for_yest) + " репостов!"

    vk_bot.send_message_to_chat(config.chat_for_notification_id, text, token)