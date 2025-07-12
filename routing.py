from django.urls import path
import core


weburlpatterns = [
    path("ws/realtime/", core.WebSock.as_asgi(), name="实时数据"),
]