import json
import time
from typing import Any
from lib.database import Redis, MySQL
from lib.database.mysql import Condition
from lib.database.mysql import Field, constant
from lib.sys.processing import Queue
from lib import Logger, Catch

from core._models.detial import DetialIndex, DetialViews

# MYSQL 数据更新队列
mysql_update_queue: Queue =  Queue()

class DataBase:
    """
        # 数据库操作模块： 实现数据库相关操作，异步
    """
    logger = Logger("data")             # 导入日志写入模块
    catch = Catch(logger)               # 导入异常捕获模块
    database = MySQL()                  # 导入MySQL工作台
    cache = Redis(                      # 导入Reids工作台
        # 设置捕获类型
        connect=False, 
        timeout=False,
        data=False
    ) 

    def __init__(self):

        # 检查数据库依赖的MySQL表
        if not self.check_tables("detialindex"):
            self.logger.record(3, "MYSQL detialindex 表 不存在")
            raise "MYSQL detialindex 表 不存在"
        
        # 导入索引表
        self.table_detialindex = self.database.workbook("detialindex")
        self.table_userdata = self.database.workbook("userdata")

    def check_tables(self, table:str):                          # 校验MySQL表存在
        return table in self.database.tables()
    
    def get_detial_message(self, detial:str) -> dict:           # 文章数据获取(Redis)
        self.logger.record(1, f"read detial:{detial} information from detialindex")
        detialdata = self._hget_cache_(detial)
        if detialdata is None:
            # 缓存相关数据时，该从MySQL读取数据
            detialdata = self._get_detial_message(detial)
            # 将数据写入缓存, 供下次读取使用
            self.set_detial_message(detial, detialdata)
        return self.jsonloads(detialdata)
    
    def _get_detial_message(self, detial:str) -> dict:          # 文章数据获取(MYSQL)
        # 设置检索条件
        condition = Condition(self.table_detialindex.detial == detial)

        try:
            # 获取文章名称、预览数据连接、同浏览量
            detial, viewslink, count = self.table_detialindex.select(condition=condition)[0]
        except (TypeError, ValueError):
            # 处理查询不到文章时的异常(设置默认值)
            detial, viewlink, count = detial, None, None

        # 查询view表， 读取单个用户浏览次数
        if viewlink and self.check_tables(viewslink):
            # 获取view工作簿
            viewdata = self.database.workbook(viewslink)
        else:
            # 创建view工作簿
            viewdata = self._create_viewlink_(f"{detial}_views")

        # 读取view表数据
        viewdata = viewdata.select()

        # 返回文章信息，处理空数据状态, 数据兼容缓存格式
        return  {
                "views": {usrid: times for usrid, times in viewdata} if viewdata else dict(),
                "count": count if count else 0
            }

    def set_detial_message(self, detial:str, data:dict):        # 文章数据写入(Redis)
        self.logger.record(1, f"update detial:{detial} data from detialindex")
        self._hset_cache_(detial, data)

        # 异步 更新MYSQL 保存数据到磁盘
        mysql_update_queue.put((detial, data, time.time()))

    def _set_detial_data(self, detial:str, data:dict):          # 文章数据写入(MySQK): 添加数据更新任务队列 实现数据异步更新 redis 数据 写入 mysql
        self.logger.record(1, f"update detial: {detial} form cache")
        
        # 数据预处理，获取view表链接，提取view表数据，文章统计数据
        viewlink = f"{detial}_views"
        viewdata = data['views'].items()
        count = data['count']

        # 更新文章数据
        try:
            self.table_detialindex.insert((detial, viewlink, count))
        except Exception:
            self.table_detialindex.update((detial, viewlink, count))

        # 更新view表数据
        viewtable = self.database.workbook(viewlink)
        for item in viewdata:
            try:
                viewtable.insert(tuple(item))
            except Exception:
                viewtable.update(tuple(item))

    def check_now_userdata(self):                               # 查询全部用户数据
        # 读取缓存用户数据
        userids = self.cache.lrange("usrids")
        if userids is None:
            # 读取MySQL用户数据
            userids = self.table_userdata.select("usrid")
            # 数据写入缓存
            self.cache.rpush("usrids", *userids)
            # 设置过期时间，如果十秒没有查询，清理缓存
            self.cache.expire("usrids", 10)
        
        # 统一数据格式，返回列表类型
        if not isinstance(userids, list):
            userids = list(userids)
        return self.jsondumps(userids)

    def check_now_detials(self):                                # 查询全部文章索引
        # 读取缓存文章索引
        detials = self.cache.lrange("detials")
        if detials is None:
            # 查询MySQL文章索引
            detials = self.table_detialindex.select("detial")
            # 数据写入缓存
            self.cache.rpush("detial", *detials)
            # 设置过期时间，如果十秒没有查询，清理缓存
            self.cache.expire("detials", 10)

        # 统一数据格式，返回列表类型
        if not isinstance(detials, list):
            detials = list(detials)
        return self.jsonloads(detials)
    
    def check_now_hitrate(self):                                # 查询当前缓存命中率
        info = self.cache.info("stats")
        hits = info['keyspace_hits']
        misses = info['keyspace_misses']
        return round(hits / (hits + misses), 2) * 100
    
    def jsonloads(self, strdata:str) -> object:                 # 数据转换模块: JSON => Python
        return self.cache.loads(strdata)

    def jsondumps(self, data: object):                          # 数据转换模块: Python => JSON
        return json.dumps(data, ensure_ascii=False, indent=4)
    
    def _create_viewlink_(self, viewslink):                     # 创建view表模板
        return self.database.create(
                    viewslink, 
                    fetchs=(
                        # 设置字段名，字段类型，字段属性
                        Field("usrid", constant.Int, constant.PRIMARY),
                        Field("count", constant.Int)
                    )
                )
    
    # 缓存数据读写， 设置异常捕获，实现异常分级功能
    @catch.DataBase(cache=cache, disk=database, error_callback=_get_detial_message)
    def _hget_cache_(self, name:str):                           # 缓存读取, 设置异常回调函数(_get_detial_message)
        # 设置异常回调函数时，保证 回调函数参数 与 原函数 一致
        # raise TimeoutError("测试分级效果")
        label = "detialindex"
        data = self.cache.hget(label, name)
        return self.jsonloads(data)
    
    @catch.DataBase(cache=cache, disk=database, error_callback=_set_detial_data)
    def _hset_cache_(self,name:str, data:dict):                 # 缓存写入，设置异常回调函数(_set_detial_data)
        # 设置异常回调函数时，保证 回调函数参数 与 原函数 一致
        # raise TimeoutError("测试分级效果")
        label = "detialindex"
        self.cache.hset(label, name, self.jsondumps(data))



    
    
if __name__ == "__main__":
    db = DataBase()
