import json
from .config import logger
from database import DataBase

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

        # 缓存查询数据

        # 更新redis数据
        self.usedb.set_detial_message(detial, detialdata)

    def count_usernums(self):                               # 统计所有用户人数
        usrids = self.usedb.check_now_userdata()
        logger.record(1, "统计用户人数")
        return len(usrids)

    def count_detial_all_readtimes(self, detial):           # 统计文章总阅读次数
        data = self.usedb.get_detial_message(detial)
        count =  data['count']
        return count
    
    def count_detial_one_user_readtimes(self, detial, usrid:int):  # 统计单用户阅读次数
        detial = self.usedb.get_detial_message(detial)
        try:
            count = detial['views'][usrid]
        except KeyError:
            count = 0
        return count
