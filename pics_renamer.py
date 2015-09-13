__author__ = 'onotole'


import os
import os.path
import config

path_to_dir = '/Users/onotole/yandex.disk/humordirs/humor'

counter = 1
for pic in os.listdir('/Users/onotole/yandex.disk/humordirs/humor'):
    #print pic
    try:
        if u'jpg'.encode('utf-8') in pic.lower() or u'jpeg'.encode('utf-8') in pic.lower():
            os.rename(os.path.join(path_to_dir, pic), os.path.join(path_to_dir, str(counter) + u'.jpg'.encode('utf-8')))
        if u'png'.encode('utf-8') in pic.lower():
            os.rename(os.path.join(path_to_dir, pic), os.path.join(path_to_dir, str(counter) + u'.png'.encode('utf-8')))
        counter += 1
    except OSError:
        print u"shit happens with " + pic


