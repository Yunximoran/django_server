from django.http import HttpRequest, HttpResponse
from lib.database import Redis as Cache
import asyncio


from ._form import data
from ._actions import Count

count = Count()

def realtime(request:HttpRequest):
    num = 0
    return HttpRequest({
        "count": num
    })


def demopage(request:HttpRequest, detialname:str):
    # 需要系统哪些参数
    """
        文章名称
    """
    if request.method == "GET":
        usrid = request.GET.get('usrid')
        count.add_count(detialname, usrid)
    return HttpResponse("这是一个文章详情页")