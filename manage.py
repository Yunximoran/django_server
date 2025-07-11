#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from lib import resolver
from lib.sys.processing import Process, Pool, Queue
from view._actions.config import usedb
from database import mysql_update_queue

def main(argv=sys.argv):
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(argv)


def dispose_updateserver(param):
    detial, data = param
    usedb._set_detial_data(detial, data)
    return detial

def updataserver(queue:Queue):
    tasks = {}  # 参数表
    tasktimes = {}  # 时间戳
    # 异常分级，写入MySQL，插队
    items = 0
    while True:
        # 添加时间戳校验，防止写入旧的数据
        detial, data, time = queue.get()
        items += 1
        if detial in tasktimes and time > tasktimes[detial]:
            tasktimes[detial] = time
            tasks[detial] = data
        else:
            tasktimes[detial] = time
            tasks[detial] = data

        if items >= 30:
            with Pool() as pool:
                pool.map_async(dispose_updateserver, tasks.items()).get()
            items = 0
        


if __name__ == "__main__":
    """ 场景
    - 当用户访问文章详情页时，统计用户人次、每人对应的阅读次数、总阅读次数。
    - 阅读量相关统计数据需实时显示（可以只给一个数据接口，或者简单html展示）
    - 需设计缓存更新数据库，数据库异步更新，要保证数据一致性安全，防止数据丢失或错误。
    - 系统需监控缓存命中率，redis统计、接口查询命中率百分比。
    """

    """ 要求
    1. 缓存设计：使用Redis缓存阅读量数据，减少数据库IO。
    2. 读写分离：读操作优先访问缓存，写操作异步更新数据库。
    3. 缓存命中率：优化缓存策略提高命中率，设计数据最终一致性方案。
    4. 异常分级处理：区分缓存/数据库异常级别并降级处理。
    5. 面向对象封装：模块化设计，分离缓存操作、数据库操作和异常处理。
    """

    """ 设计
    接口：

        realtime: 实时输出数据
        demopage: 测试接口
        add_count: 计算单个用户阅读次数
        get_all_count: 计算全部阅读次数
        count_usernum: 统计用户数量
    
    数据库：
        redis数据缓存
        API数据通过redis读写， 定时保存redis缓存数据（异步）

    数据表：
    文章信息表: 文章基本信息、用户浏览数据
    detailtables: {
        detial_1: {
            views {
                usrid: count
                ......
            }        
        }
        
    }
    # redis 实现： 使用Hash表： 表， 名， 数据
    # mysql 实现
        文章索引表：保存文章索引
        文章信息表：保存文章信息
        浏览信息表：保存对应文章浏览信息

    用户数据表: 用户名称、用户ID
    userdata: {
        "usrid": 用户唯一标识
        "uname": 用户名
    }

    缓存策略：
        hash表存储数据
        常规键值对做过期处理

    系统：
        监控redis缓存命中率（redis统计、接口查询命中 [百分比]）
    """

    """ 注意事项
    1、使用 Django 框架。
    2、请勿直接照搬AI生成答案，参考AI的部分请注明自己的理解！若70%以上为AI直接照搬将不再安排后续面试。
    3、请在 Git 中进行多次提交并标注每次改动与原因。
    4、若是本地迭代修改，需在文档里记录每次改动的内容与原因。
    """

    _conf = resolver("services")
    _host = _conf.search("host").data
    _port = _conf.search('port').data
        
    Process(target=updataserver, args=(mysql_update_queue,)).start()
    sys.argv = [sys.argv[0], "runserver", "{}:{}".format(_host, _port)]
    main(sys.argv)

    # http://localhost:8000/demopage/eeee/?uname=yumo&usrid=123