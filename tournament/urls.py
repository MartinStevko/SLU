from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from tournament.views import TournamentListView, TournamentDetailView

app_name = 'tournament'

urlpatterns = [
    #path('<int:pk>/submit/', staff_member_required(SubmitFormView.as_view()), name='submit'),
    path('<int:pk>/detail/', TournamentDetailView.as_view(), name='detail'),
    path('', TournamentListView.as_view(), name='list'),
]
