from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import *

app_name = 'user'

urlpatterns = [
    path('login/sent/', LoginWaitingView.as_view(), name='login_sent'),
    path('login/', LoginView.as_view(), name='login'),
    path('<int:pk>/<str:key>/login/', LoginKeyView.as_view(), name='authenticate'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
