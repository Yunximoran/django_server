import json
from database import DataBase
from ..config import USERDATA

class Count:
    def __init__(self):
        self.usedb = DataBase()
        self.count = 0


    def add_count(self, detial:str, usrid:int):            # 更新用户浏览次数
        # 获取数据
        detialdata = self.usedb.get_detial_message(detial)
        # 更新浏览次数
        views_data = detialdata['views']
        # print("view_data", views_data, type(views_data))
        # for usridi in views_data:
        #     print("usrid", usridi, type(usrid))
        # print("bool", usrid in views_data)
        if usrid in views_data:
            views_data[usrid] += 1
        else:
            views_data[usrid] = 1
        detialdata['count'] += 1
        # 更新redis数据
        print("hit rate: ", self.usedb.hitrate())
        self.usedb.update_detial_message(detial, detialdata)

    def count_usernums(self):                               # 统计所有用户人数
        alluserdata = self.usedb.get(USERDATA)
        return len(alluserdata)
    
    def count_detial_all_readtimes(self, detial):           # 统计文章总阅读次数
        detialdata = self.usedb.get("detialindex")
        count = 0

        for detial in detialdata:
            for times in detial['view'].values():
                count += times

        return count

    def count_detial_touser_readtimes(self, detial, usrid):  # 统计单用户阅读次数
        detialdata = self.getinfo(detial, usrid)
        return detialdata['view'][usrid]
    
