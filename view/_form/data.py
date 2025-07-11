from django import forms


class FormDetialData(forms.Form):
    name = forms.CharField(max_length=100)      # 文章名称
    page = forms.CharField(max_length=100)      # 文章页面
    link = forms.CharField(max_length=100)      # 文章链接
    nums = forms.CharField(max_length=20)       # 文章页码


class FormUserData(forms.Form):
    uname = forms.CharField(max_length=100)     # 用户名
    usrid = forms.CharField(max_length=100)     # 用户id