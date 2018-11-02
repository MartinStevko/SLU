from django.urls import path, re_path

from . import views

app_name = 'diary'

urlpatterns = [
    path('prihlasovanie/', views.prihlasovanie, name='prihlasovanie'),
    path('index/', views.index, name='index'),
    path('', views.no_match, name='no_match'),
]
