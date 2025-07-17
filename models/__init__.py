import os, django
from django.contrib import admin

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings")
django.setup()

from .detial import *
from .userdata import *


admin.site.register([DetialIndex, DetialViews, UserData])