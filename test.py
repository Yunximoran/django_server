import requests
from lib.sys.processing import Pool
import random

baseurl = "http://localhost:8000/" #

# baseurl + demodetial/{test_detial[:]}

def get_detial():
    test_detial = "abcdefghijklmn"
    return "".join([
        test_detial[random.randint(0, 13)],
        test_detial[random.randint(0, 13)],
        test_detial[random.randint(0, 13)],
        test_detial[random.randint(0, 13)]
    ])
    # 测试用户页面

def get_params():
    return {"usrid": 123}

def test_api(x=0):
    detial = get_detial()
    params = get_params()
    url = f"{baseurl}demopage/eeee"
    return  requests.get(url, params=params)


def realtime():
    requests.get()

if __name__ == "__main__":

    with Pool(10) as pool:
        results = pool.map_async(test_api, range(0, 50)).get()
    for res in results:
        print(res.text)
