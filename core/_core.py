from django.http import HttpRequest, HttpResponse
from lib.database import Redis as Cache
import asyncio


from ._form import data
from ._actions import Count, Temp

count = Count()
temp = Temp()

def realtime(request:HttpRequest):
    hitrate = count.usedb.hitrate()
    all_data = count.count_detial_all_readtimes("eeee")

    return HttpResponse(count.usedb.jsondumps({
        "缓存命中率": hitrate,
        "数据": all_data
    }))

def demopage(request:HttpRequest, detialname:str):
    # 需要系统哪些参数
    """
        文章名称
    """
    if request.method == "GET":
        usrid = request.GET.get('usrid')
        count.cache
        count.add_count(detialname, usrid)
    return HttpResponse("这是一个文章详情页")