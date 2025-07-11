import requests


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