from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

app_name = 'registration'

from django.views.generic import View

urlpatterns = [
    #path('<int:pk>/submit/', staff_member_required(SubmitFormView.as_view()), name='submit'),
    path('create/', View.as_view(), name='create'),
]
