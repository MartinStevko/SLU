from django.urls import path, re_path

from . import views

app_name = 'diary'

urlpatterns = [
    path('', views.index, name='index'),
]
