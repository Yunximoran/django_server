# import os, django
# from django.db import connection
# from django.db import models


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings")
# django.setup()

# class DetialIndex(models.Model):
#     detial = models.CharField(max_length=32, primary_key=True)
#     count = models.IntegerField()

        
    
# class DetialViews(models.Model):
#     detial = models.ForeignKey(DetialIndex, on_delete=models.CASCADE)
#     usrid = models.IntegerField()
#     count = models.IntegerField()

#     class Meta:
#         unique_together  = ("detial", "usrid")

# class UserData(models.Model):
#     usrid = models.IntegerField(primary_key=True)
#     uname = models.CharField(max_length=32)



# # if __name__ == '__main__':
# #     DetialIndex.objects.exclude