from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

app_name = 'tournament'

from django.views.generic import ListView

urlpatterns = [
    #path('<int:pk>/submit/', staff_member_required(SubmitFormView.as_view()), name='submit'),
    path('', ListView.as_view(), name='list')
]
