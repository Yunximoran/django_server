import json

from lib.database import Redis, MySQL
from lib.database.mysql import Condition
from lib.database.mysql import Field, constant

from lib import Logger, Catch

logger = Logger("data")
catch = Catch(logger)
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

        # 定义文章数据表
        if not self.__check_tables("detialindex"):
            logger.record(3, "MYSQL detialindex 表 不存在")
            raise "MYSQL detialindex 表 不存在"
        self.table_detialtables = self.database.workbook("detialindex")

    def __check_tables(self, table):
        return table in self.database.tables()

    def get_detial_message(self, detial):
        logger.record(1, f"read detial:{detial} information from detialtables")
        detialdata = self.cache.hget("detialtables", detial)
        if detialdata is None:
            # 缓存相关数据时，该从MySQL读取数据
            detialdata = self._get_detial_message(detial)

            # 将数据写入缓存, 供下次读取使用
            self.hset("detialindex", detial, detialdata)
        return detialdata
    
    def _get_detial_message(self, detial):
        # 设置检索条件
        condition = Condition(self.table_detialtables.detial == detial)

        try:
            # 获取文章名称、预览数据连接、同浏览量
            detial, viewslink, count = self.table_detialtables.select(condition=condition)[0]
        except ValueError:
            # 处理查询不到文章时的异常
            detial, viewlink, count = detial, None, None

        # 查询view表， 读取单个用户浏览次数
        if viewlink and self.__check_tables(viewslink):
            viewdata = self.database.workbook(viewslink)
        else:
            viewdata = self.__create_viewlink(f"{detial}_{viewslink}")

        # 读取view表数据
        viewdata = viewdata.select()
        return {
            detial: {
                "views": {usrid: times for usrid, times in viewdata} if viewdata else {},
                "count": count if count else 0          # count为假，新文章，无浏览
            }
        }

    def update_detial_message(self, detial, data):
        # 获取当前数据
        logger.record(1, f"update detial:{detial} data from detialtables")
        self.hset("detialtables", detial, data)

    def __create_viewlink(self, viewslink):
        return self.database.create(
                    viewslink, 
                    fetchs=(
                        Field("usrid", constant.Int, constant.PRIMARY),
                        Field("count", constant.Int)
                    )
                )

    def hset(self, name, key, val):
        rval = self.jsondumps(val)
        self.cache.hset(name, key, rval)

    def hget(self, name, key):
        # detialtables
        cache_data = self.cache.hget(name, key)
        if cache_data is None:
            # 处理无缓存事件
            cache_data = {

            }
            if name not in self.database.tables():
                self.database.create(name, key)
                raise KeyError(f"没有MySQL表 {name}")
            

            tabel = self.database.workbook(name)
            data = tabel.select()
            fields = tabel.fields.copy()
            for item in data:
                for field, val in zip(fields, item):
                    pass

        return self.jsonloads(data)
    

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
    # db = DataBase()
    # data = db.hget("userdata", "uname")

    # print("", data)
    db = MySQL("djangodata")
    table = db.workbook("userdata")
    # print(table.usrid)
    # print(table.uname)
    name = table.select(condition=Condition("usrid = 66"))

    d = {1: 2}
    if name:
        print(d)
    # print(type(name[0][0]))
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