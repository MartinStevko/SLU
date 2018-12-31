from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from tournament.views import *

app_name = 'tournament'

urlpatterns = [
    #path('<int:pk>/submit/', staff_member_required(SubmitFormView.as_view()), name='submit'),
    path('<int:pk>/detail/', TournamentDetailView.as_view(), name='detail'),
    path('<int:pk>/match/list/', TournamentMatchesView.as_view(), name='match_list'),
    path('<int:tournament>/match/<int:pk>/', MatchDetailView.as_view(), name='match_detail'),
    path('<int:pk>/player/stats/', PlayerStatsView.as_view(), name='player_stats'),
    path('<int:pk>/results/', TournamentResultsView.as_view(), name='results'),
    path('', TournamentListView.as_view(), name='list'),
]
