import json
from .config import logger
from database import DataBase
from asgiref.sync import sync_to_async

class Count:
    usedb = DataBase()
    def __init__(self):
        self.count = 0


    def add_count(self, detial:str, usrid:int):            # 更新用户浏览次数
        # 获取数据
        detialdata = self.usedb.get_detial_message(detial)

        # 更新浏览次数
        views_data = detialdata['views']
        
        if usrid in views_data:
            views_data[usrid] += 1
        else:
            views_data[usrid] = 1
        detialdata['count'] += 1
        print(detialdata)

        # 更新redis数据
        self.usedb.set_detial_message(detial, detialdata)

    @sync_to_async
    def count_usernums(self):                               # 统计所有用户人数
        usrids = self.usedb.check_now_userdata()
        return len(usrids)

    @sync_to_async
    def count_detial_all_readtimes(self, detial):           # 统计文章总阅读次数
        return self.usedb.check_detial_views(detial)
    
    @sync_to_async
    def count_detial_one_user_readtimes(self, detial, usrid):  # 统计单用户阅读次数
        return self.usedb.check_detial_user_views(detial, usrid)
