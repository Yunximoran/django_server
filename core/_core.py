from django.http import HttpRequest, HttpResponse
from lib.database import Redis as Cache
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio
import urllib.parse

from ._form import data
from ._actions import Count, Temp

count = Count()
temp = Temp()

class WebSock(AsyncWebsocketConsumer):
    # count = Count()
    async def connect(self):
        query_string = self.scope["query_string"].decode("utf-8")
        query_params = urllib.parse.parse_qs(query_string)
        
        self.detial = query_params.get("detial", [""])[0]
        self.usrid = int(query_params.get("usrid", [""])[0] )       
        self.runing = True
        print(self, self.detial, self.usrid)
        if not self.detial or not self.usrid:
            await self.close(code=400)
            return

        await self.accept()
        self.push_task = asyncio.create_task(self.push_real_time_data())

    def disconnect(self, close_code):
        self.runing = False
        if hasattr(self, "push_task"):
            self.push_task.cancel()

    async def push_real_time_data(self):
        while self.runing:
            try:
                hitrate = count.usedb.hitrate()
                all_data = count.count_detial_all_readtimes(self.detial)
                readt = count.count_detial_one_user_readtimes(self.detial, self.usrid)
                userslen = count.count_usernums()
                msg = count.usedb.jsondumps({
                    "缓存命中率": hitrate,
                    "文章总浏览次数": all_data,
                    "用户浏览次数": readt,
                    "用户人数": userslen
                })
                await self.send(msg)
            except asyncio.CancelledError:
                
                break
            except Exception as e:
                await self.close(code=1011)
                break
            await asyncio.sleep(1)

    def receive(self, text_data=None, bytes_data=None):
        return super().receive(text_data, bytes_data)

def demopage(request:HttpRequest, detialname:str):
    # 需要系统哪些参数
    """
        文章名称
    """
    if request.method == "GET":
        usrid = request.GET.get('usrid')
        count.add_count(detialname, usrid)
    return HttpResponse("这是一个文章详情页")