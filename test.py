import requests
from lib.sys.processing import Pool
import random

baseurl = "http://localhost:8000/"

# baseurl + demodetial/{test_detial[:]}
test_detial = "abcdefghijklmn"
    # 测试用户页面


# data in test_users
test_users = [
    {
        "usrid": 123
    },
    {
        "usrid": 234
    },
    {
        "usrid": 345
    }
]

def test_api(x):
    detial = test_detial[random.randint(0, len(test_detial)) - 1] * 4
    params = test_users[random.randint(0, 2)] 
    print(params)
    return requests.get(f"{baseurl}demopage/{detial}", params=params)

if __name__ == "__main__":
    with Pool() as pool:
        results = pool.map_async(test_api, range(0, 100)).get()
    
    for res in results:
        print(res)
