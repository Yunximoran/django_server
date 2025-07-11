import json
import time
from lib.database import Redis, MySQL
from lib.database.mysql import Condition
from lib.database.mysql import Field, constant
from lib.sys.processing import Process
from lib.sys.processing import Queue

from lib import Logger, Catch

logger = Logger("data")
catch = Catch(logger)
mysql_update_queue: Queue =  Queue()

class DataBase:

    cache = Redis(connect=False, timeout=False, data=False)
    database = MySQL()

    def __init__(self):
        # 定义文章数据表
        if not self.__check_tables("detialindex"):
            logger.record(3, "MYSQL detialindex 表 不存在")
            raise "MYSQL detialindex 表 不存在"
        
        self.table_detialindex = self.database.workbook("detialindex")

    def __check_tables(self, table):
        return table in self.database.tables()
    
    def get_detial_message(self, detial) -> dict:
        logger.record(1, f"read detial:{detial} information from detialindex")
        detialdata = self._get_cache_("detialindex", detial)
        if detialdata is None:
            # 缓存相关数据时，该从MySQL读取数据
            detialdata = self._get_detial_message(detial)

            # 将数据写入缓存, 供下次读取使用
            self.set_detial_message(detial, detialdata)

        return self.jsonloads(detialdata)
    
    def _get_detial_message(self, detial):
        # 设置检索条件
        condition = Condition(self.table_detialindex.detial == detial)

        try:
            # 获取文章名称、预览数据连接、同浏览量
            detial, viewslink, count = self.table_detialindex.select(condition=condition)[0]

        except (TypeError, ValueError):
            # 处理查询不到文章时的异常
            detial, viewlink, count = detial, None, None

        # 查询view表， 读取单个用户浏览次数
        if viewlink and self.__check_tables(viewslink):
            viewdata = self.database.workbook(viewslink)
        else:
            viewdata = self.__create_viewlink(f"{detial}_views")

        # 读取view表数据
        viewdata = viewdata.select()
        return  {
                "views": {usrid: times for usrid, times in viewdata} if viewdata else dict(),
                "count": count if count else 0          # count为假，新文章，无浏览
            }

    def set_detial_message(self, detial, data):
        # 获取当前数据
        logger.record(1, f"update detial:{detial} data from detialindex")
        data = self._set_cache_("detialindex", data, detial)
        # 异步 更新MYSQL 保存数据到磁盘
        mysql_update_queue.put((detial, data))
        # self._set_detial_data(detial, data)

    def _set_detial_data(self, detial, data):        # 异步更新数据策略 redis 数据 写入 mysql
        # 获取view链接表
        print("LOGGER UPDATE MYSQL")
        viewlink = f"{detial}_views"
        viewdata = data['views'].items()
        count = data['count']

        # 更新索引数据
        try:
            self.table_detialindex.insert((detial, viewlink, count))
        except Exception:
            self.table_detialindex.update((detial, viewlink, count))
        # 更新链接表数据
        viewtable = self.database.workbook(viewlink)
        for item in viewdata:
            try:
                viewtable.insert(tuple(item))
            except Exception:
                viewtable.update(tuple(item))

    def __create_viewlink(self, viewslink):
        return self.database.create(
                    viewslink, 
                    fetchs=(
                        Field("usrid", constant.Int, constant.PRIMARY),
                        Field("count", constant.Int)
                    )
                )

    def jsonloads(self, strdata):
        return self.cache.loads(strdata)

    def jsondumps(self, data):
        return json.dumps(data, ensure_ascii=False, indent=4)
    
    @catch.DataBase(cache=cache, disk=database, error_callback=_get_detial_message)
    def _get_cache_(self, label, name=None):
        if name is None:
            data = self.cache.get(label)
        else:
            data = self.cache.hget(label, name)
        return self.jsonloads(data)
    
    @catch.DataBase(cache=cache, disk=database, error_callback=_set_detial_data)
    def _set_cache_(self, label, data, name=None):
        if name is None:
            status = self.cache.set(label, self.jsondumps(data))
        else:
            status = self.cache.hset(label, name, self.jsondumps(data))
        return status
    
    
    def hitrate(self):            # 缓存命中率
        info = self.cache.info("stats")
        hits = info['keyspace_hits']
        misses = info['keyspace_misses']
        return round(hits / (hits + misses), 2) * 100
    
if __name__ == "__main__":
    db = DataBase()
    # data = db.hget("userdata", "uname")

    # print("", data)
    # db = MySQL("djangodata")
    # table = db.workbook("userdata")
    # # print(table.usrid)
    # # print(table.uname)
    # name = table.select(condition=Condition("usrid = 66"))

    # d = {1: 2}
    # if name:
    #     print(d)
    d = {1: 2}
    print(tuple(d.items()))

    print(db.cache.keys())
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