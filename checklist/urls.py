from django.urls import path

from checklist.views import *

app_name = 'checklist'

urlpatterns = [
    path('tournament/<int:pk>/task/', ChangeTaskAjaxView.as_view(), name='ajax_edit_task'),
    path('tournament/<int:pk>/', ChecklistDetailView.as_view(), name='todo'),
]
