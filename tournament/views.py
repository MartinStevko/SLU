from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from tournament.models import Tournament


class TournamentListView(ListView):
    template_name = 'tournament/tournament_list.html'

    model = Tournament
    context_object_name = 'previous_tournaments'

    paginate_by = 1

    queryset = Tournament.public.get_previous()

    def get_context_data(self, **kwargs):
        context = super(TournamentListView, self).get_context_data(**kwargs)
        next_tournaments = Tournament.public.get_next()

        tournament_tags = []
        # [[last_places, registraion_full, registration_open],]

        for t in next_tournaments:
            tournament_tags.append([
                (t.max_teams <= t.team_count()+3),
                (t.max_teams <= t.confirmed_team_count()+3),
                t.is_registration_open(),
            ])

        context.update({
            'next_tournaments': zip(next_tournaments, tournament_tags),
            'detail': False,
        })
        return context


class TournamentDetailView(TemplateView):
    pass
