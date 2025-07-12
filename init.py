from lib.database import MySQL
from lib.database.mysql import constant, Field

wb = MySQL()

# 创建文章表
def create_detail():
    detial = Field("detial", constant.VarChar(255), constant.PRIMARY)
    views = Field("views", constant.VarChar(255))
    count = Field("count", constant.Int)
    wb.create("detialindex", (detial, views, count))


# 创建用户表
def create_users():
    usrid = Field("usrid", constant.Int, constant.PRIMARY)
    uname = Field("uname", constant.VarChar(255))
    wb.create("userdata", (usrid, uname))

if __name__ == "__main__":
    create_detail()
    create_users()




