from django.http import HttpRequest, HttpResponse
from lib.database import Redis as Cache

from ._actions import Count
cache = Cache()
count = Count()

def realtime(request:HttpRequest):
    num = 0
    return HttpRequest({
        "count": num
    })


def demopage(request:HttpRequest):
    if request.content_type == "GET":
        uname = request.GET.get("name")
        count.add_user_count(uname)

    return HttpResponse("这是一个文章详情页")