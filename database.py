import json
import time
from typing import Any

from lib.database import Redis
from lib.sys.processing import Queue
from lib import Logger, Catch

from models.detial import *
from models.userdata import *

# MYSQL 数据更新队列
mysql_update_queue: Queue =  Queue()

class DataBase:
    """
        # 数据库操作模块： 实现数据库相关操作，异步
    """
    logger = Logger("data")             # 导入日志写入模块
    catch = Catch(logger)               # 导入异常捕获模块
    cache = Redis(                      # 导入Reids工作台
        # 设置捕获类型
        connect=False, 
        timeout=False,
        data=False
    ) 

    def __init__(self):
        pass
    
    def get_detial_message(self, detial:str) -> dict:           # 文章数据获取(Redis)
        self.logger.record(1, f"read detial:{detial} information from detialindex")
        detialdata = self._hget_cache_(detial)
        if not detialdata:
            # 缓存相关数据时，该从MySQL读取数据
            detialdata = self._get_detial_message(detial)

            # 将数据写入缓存, 供下次读取使用
            self.set_detial_message(detial, detialdata)
        return self.jsonloads(detialdata)
    
    def _get_detial_message(self, detial:str) -> dict:          # 文章数据获取(MYSQL)
        try:
            # 获取文章名称、预览数据连接、同浏览量
            detialindex = DetialIndex.objects.get(detial=detial)
            views = {data.usrid: data.count for data in DetialViews.objects.filter(detial=detialindex)}
            count = detialindex.count
        except DetialIndex.DoesNotExist:
            detial, views, count = detial, False, False
        return  {
                "views": views if views else dict(),
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
        viewdata = data['views'].items()
        count = data['count']
        
        detialtable, _  = DetialIndex.objects.update_or_create(detial=detial, defaults={"count":count})
        
        # 更新view表数据
        for usrid, count in viewdata:
            DetialViews.objects.update_or_create(detial=detialtable, usrid=usrid, defaults={"count":count})
            if not UserData.objects.filter(usrid=usrid).exists():
                UserData.objects.create(usrid=usrid, uname="yumo")

        
    def check_detial_views(self, detial:str):
        self.logger.record(1, f"read detial: {detial}")

        count = self.cache.hget(f"check_count_{detial}", "count")
        if not count:
            try:
                count = DetialIndex.objects.get(detial=detial).count
            except DetialIndex.DoesNotExist:
                count = 0

            self.cache.hset(f"check_count_{detial}", "count", count)
            self.cache.expire(f"check_count_{detial}", 3)

        return count
    
    def check_detial_user_views(self, detial, usrid):
        self.logger.record(1, f"fitter out {usrid} from {detial}")
        ucount = self.cache.hget(f"check_count_{detial}", usrid)     
        if not ucount:
            try:
                ucount = DetialViews.objects.get(detial=detial, usrid=usrid).count
            except DetialViews.DoesNotExist:
                ucount = 0
            self.cache.hset(f"check_count_{detial}", usrid, ucount)
            self.cache.expire(f"check_count_{detial}", 3)
        return ucount
    
    def check_now_userdata(self):                               # 查询全部用户数据
        # 读取缓存用户数据
        users = self.cache.lrange("usrids")
        if not users:
            # 读取MySQL用户数据
            users = [user.usrid for user in UserData.objects.all()]
            print(users)
            # 数据写入缓存
            self.cache.rpush("usrids", *users)
            # 设置过期时间，如果十秒没有查询，清理缓存
            self.cache.expire("usrids", 3)
    
        # 统一数据格式，返回列表类型
        if not isinstance(users, list):
            users = list(users)
        return users
    
    def check_now_hitrate(self):                                # 查询当前缓存命中率
        info = self.cache.info("stats")
        hits = info['keyspace_hits']
        misses = info['keyspace_misses']
        return round(hits / (hits + misses), 2) * 100
    
    def jsonloads(self, strdata:str) -> object:                 # 数据转换模块: JSON => Python
        return self.cache.loads(strdata)

    def jsondumps(self, data: object):                          # 数据转换模块: Python => JSON
        return json.dumps(data, ensure_ascii=False, indent=4)
    
    # 缓存数据读写， 设置异常捕获，实现异常分级功能
    @catch.DataBase(cache=cache, disk=None, error_callback=_get_detial_message)
    def _hget_cache_(self, name:str):                           # 缓存读取, 设置异常回调函数(_get_detial_message)
        # 设置异常回调函数时，保证 回调函数参数 与 原函数 一致
        # raise TimeoutError("测试分级效果")
        label = "detialindex"
        data = self.cache.hget(label, name)
        return self.jsonloads(data)
    
    @catch.DataBase(cache=cache, disk=None, error_callback=_set_detial_data)
    def _hset_cache_(self,name:str, data:dict):                 # 缓存写入，设置异常回调函数(_set_detial_data)
        # 设置异常回调函数时，保证 回调函数参数 与 原函数 一致
        # raise TimeoutError("测试分级效果")
        label = "detialindex"
        self.cache.hset(label, name, self.jsondumps(data))
        self.cache.expire("detialindex", 3)




    
    
if __name__ == "__main__":
    db = DataBase()
