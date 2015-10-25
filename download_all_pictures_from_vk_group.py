__author__ = 'onotole'


import config
import vk_bot


vk_group_url = "http://vk.com/instagram_luxury"
vars = [vk_group_url.split("/")[-1]]
print vk_bot.get_all_posts_from_group_by_url(vk_group_url, vk_bot.module_save_picture_from_post, vars,
                                             vk_bot.processing_post_return_true, vk_bot.token)