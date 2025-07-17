from django.db import connection
from django.db import models



class UserData(models.Model):
    usrid = models.IntegerField(primary_key=True)
    uname = models.CharField(max_length=32)

    class Meta:
        db_table = "userdata"

# if __name__ == '__main__':
#     DetialIndex.objects.exclude