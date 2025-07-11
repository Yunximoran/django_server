from django.http import HttpRequest, HttpResponse


def count_checknum(request:HttpRequest):            # 统计浏览数量
    if request.content_type == "GET":
        return HttpResponse(1)
    return HttpResponse(None)