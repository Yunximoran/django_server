import requests
import asyncio
from asgiref.sync import sync_to_async

baseurl = "http://localhost:8000/"

# baseurl + demodetial/{test_detial[:]}
test_detial = [
    # 测试用户页面
    "eeee",
    "aaaa",
    "cccc"
]

# data in test_users
test_users = [
    {
        "uanme": "yumo_1",
        "usrid": 123
    },
    {
        "uanme": "yumo_2",
        "usrid": 234
    },
    {
        "uanme": "yumo_3",
        "usrid": 345
    }
]
from lib.sys.processing import Process
import time

def worker():
    time.sleep(10)

Process(target=worker).start()
if __name__ == "__main__":
    from lib.sys.processing import Process
    async def worker():
        print("hello")
        await asyncio.sleep(10)
    
    asyncio.run(worker())

    print("hello")
    # get.run_forever()