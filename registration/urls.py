from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from registration.views import *

app_name = 'registration'

urlpatterns = [
    path('create/school/', SchoolRegistrationView.as_view(), name='create_school'),
    path('create/teacher/', TeacherRegistrationView.as_view(), name='create_teacher'),
    path('create/team/', TeamRegistrationView.as_view(), name='create_team'),
    path('create/<int:pk>/', registration_redirect, name='create'),
    path('confirm/<str:identifier>/', confirmation_redirect, name='confirm'),
    path('<int:pk>/change/', ChangeTeamView.as_view(), name='change')
]
