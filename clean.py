from lib.database import MySQL, Redis
import re


cdb = Redis()
db = MySQL()

a = db.tables()
cdb.delete("detialindex")

for tn in a:
    if re.match(r".*?_views", tn):
        print(tn)
        db.delete(tn)
    else:
        table = db.workbook(tn)
        table.delete()
    # break