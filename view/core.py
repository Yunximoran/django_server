from django.http import HttpRequest, HttpResponse
from lib.database import Redis as Cache


from ._form import data
from ._actions import Count
cache = Cache()
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
        uname = request.GET.get("uname")
        usrid = request.GET.get('usrid')
        count.add_count(detialname, uname, usrid)
        # count.add_user_count(uname)
        print(detialname, uname, usrid)
    return HttpResponse("这是一个文章详情页")