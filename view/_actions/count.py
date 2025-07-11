import json
from lib.database import Redis as Cache
from ..config import USERDATA

class Count:
    def __init__(self):
        self.cache = Cache()
        self.count = 0

    def get_userdata(self, uname):              # 读取缓存中的用户数据
        userdata = self.cache.hget(USERDATA, uname)
        if userdata is None:
            # 新用户获取改用为第一次预览该页面 -> 初始化用户数据
            userdata = {
                "uname": uname,
                "count": 0
            }
            self.cache.hset(USERDATA, uname, json.dumps(userdata, ensure_ascii=False, indent=4))
        return self.cache.loads(userdata)

    def add_user_count(self, uname):            # 更新用户浏览次数
        userdata = self.get_userdata(uname)
        userdata['count'] += 1
        self.cache.hset(USERDATA, uname, json.dumps(userdata, ensure_ascii=False, indent=4))

    def count_users(self):               # 统计所有用户人数
        alluserdata = self.cache.get(USERDATA)
        count = 0
        for userdata in alluserdata:
            data = self.cache.loads(userdata)
            count += data['count']
        return count
    
    def count_user_readtimes(self, uname):  # 统计用户数量
        userdata = self.get_userdata(uname)
        return userdata['count']
