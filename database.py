import json
from lib.database import Redis, MySQL
from lib.database.mysql import Condition


class DataBase:
    __SAVEDATA = [      # 需要保存的数据表
        "userdata",
        "detial"
    ]

    usrtable = {
        "uname": "",
        "usrid": ""
    }
    def __init__(self):
        self.cache = Redis()
        self.database = MySQL()

    def init_userdata(self):
        pass

    def hset(self, name, key, val):
        rval = self.jsondumps(val)
        self.cache.hset(name, key, rval)

    def hget(self, name, key):
        cache_data = self.cache.hget(name, key)
        if cache_data is None:
            # 处理无缓存事件
            if name not in self.database.tables():
                raise KeyError(f"没有MySQL表 { name }")
            
            tabel = self.database.workbook(name)
            data = tabel.select((key, ))
        return self.jsonloads(data)
    
    def parsemysql(self, data):
        pass

    def upadte(self):   # 更新MySQL数据
        pass

    def get(self):
        pass

    def set(self):
        pass

    def addcolumn(self, tbn, cln, val):
        pass

    def jsonloads(self, strdata):
        return self.cache.loads(strdata)

    def jsondumps(self, data):
        return json.dumps(data, ensure_ascii=False, indent=4)
    

    def hitrate(self):            # 缓存命中率
        info = self.cache.info("stats")
        hits = info['keyspace_hits']
        misses = info['keyspace_misses']
        return round(hits / (hits + misses), 2) * 100
if __name__ == "__main__":
    db = DataBase()
    data = db.hget("userdata", "uname")
    print("", data)
    # db = MySQL("djangodata")
    # table = db.workbook("userdata")
    # print(table.usrid)
    # print(table.uname)
    # name = table.select(("uname",), Condition(table.usrid == 30))
    # print(name)
    # # ls = db.tables()
    # print(ls)
    # print(table.information())
    # info = Redis().info("stats")
    # hits = info['keyspace_hits']
    # misses = info['keyspace_misses']
    # print(f"{round(hits / (hits + misses), 2) * 100}%")
    # data = Redis().loads(None)
    # print(data)