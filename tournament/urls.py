from django.urls import path

from tournament.views import *
from tournament.models import Point

app_name = 'tournament'

urlpatterns = [
    path('<int:pk>/detail/', TournamentDetailView.as_view(), name='detail'),
    path('<int:pk>/checkin/list/', CheckinListView.as_view(), name='checkin_list'),
    path('<int:pk>/checkin/scanner/key/<str:key>/', QRCheckinRedirectView.as_view(), name='checkin_scanner_redirect'),
    path('<int:pk>/checkin/scanner/', QRCheckinView.as_view(), name='checkin_scanner'),
    path('<int:pk>/checkin/<int:team>/team/', TeamCheckinView.as_view(), name='team_checkin'),
    path('<int:pk>/checkin/<int:team>/confirm/', ConfirmCheckinView.as_view(), name='confirm_checkin'),
    path('<int:pk>/spirit/score/', SpiritScoreView.as_view(), name='spirit'),
    path('<int:pk>/spirit/results/', SpiritResultView.as_view(), name='spirit_results'),
    path('<int:pk>/match/list/ajax/', JSONPointListView.as_view(), name='ajax_match_points'),
    path('<int:pk>/match/list/', TournamentMatchesView.as_view(), name='match_list'),
    path('match/<int:pk>/', MatchDetailView.as_view(), name='match_detail'),
    path('match/<int:match>/point/<int:pk>/delete/', PointDeleteView.as_view(), name='delete_point'),
    path('<int:pk>/player/stats/', PlayerStatsView.as_view(), name='player_stats'),
    path('<int:pk>/results/', TournamentResultsView.as_view(), name='results'),
    path('<int:pk>/gallery/', TournamentGalleryView.as_view(), name='gallery'),
    path('<int:pk>/documents/diplomas/', diplomas_view, name='diplomas'),
    path('<int:pk>/documents/propositions/', propositions_view, name='propositions'),
    path('', TournamentListView.as_view(), name='list'),
]
