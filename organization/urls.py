from django.urls import path, re_path

from . import views

app_name = 'diary'

urlpatterns = [
    path('prihlasovanie/', views.prihlasovanie, name='prihlasovanie'),
    path('data/admin/', views.organizacia, name='organizacia'),
    path('', views.index, name='index'),
]
