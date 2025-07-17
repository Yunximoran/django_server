import os, django
from django.db import connection
from django.db import models


class DetialIndex(models.Model):
    detial = models.CharField(max_length=32, primary_key=True)
    count = models.IntegerField()

    class Meta:
        db_table = "detialindex"
    
class DetialViews(models.Model):
    detial = models.ForeignKey(DetialIndex, on_delete=models.CASCADE)
    usrid = models.IntegerField()
    count = models.IntegerField()

    class Meta:
        db_table = "detialview"
        unique_together  = ("detial", "usrid")



# if __name__ == '__main__':
#     DetialIndex.objects.exclude