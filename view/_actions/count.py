import json
from database import DataBase
from ..config import USERDATA

class Count:
    def __init__(self):
        self.usedb = DataBase()
        self.count = 0

    def init_userdata(self, usrid):
        pass

    def init_detialdata(self, detial):
        pass

    def get_userdata(self, detial, usrid):              # 读取缓存中的用户数据
        # 获取数据
        detialdata = self.usedb.hget("detialtable", detial)
        userdata = self.usedb.hget("userdata", usrid)
        return detialdata
        # 校验数据是否存在
        # 初始化数据
        # 返回数据模板

    def add_count(self, detial, uname, usrid):            # 更新用户浏览次数
        # 获取数据
        detialdata = self.get_userdata(detial, uname, usrid)
        # 更新浏览次数
        detialdata['view'][usrid] += 1
        # 更新redis数据
        self.usedb.hset("detialtable", detial, detialdata)

    def count_usernums(self):                               # 统计所有用户人数
        alluserdata = self.usedb.get(USERDATA)
        return len(alluserdata)
    
    def count_detial_all_readtimes(self, detial):           # 统计文章总阅读次数
        detialdata = self.usedb.get("detialtable")
        count = 0

        for detial in detialdata:
            for times in detial['view'].values():
                count += times

        return count

    def count_detial_touser_readtimes(self, detial, usrid):  # 统计单用户阅读次数
        detialdata = self.get_userdata(detial, usrid)
        return detialdata['view'][usrid]
    
