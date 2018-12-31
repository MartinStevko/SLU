from django.shortcuts import render
from django.views.generic import ListView, DetailView

from tournament.models import Tournament


def get_tabs(user, isinstance):
    '''[
        (title,url,warn),
        (title,url,warn),
        (title,url,warn),
    ]'''

    return False


def get_toolbox(user, isinstance):
    '''[# toolbox
        [# tool group 1
            (tool,url),
            (tool,url),
            (tool,url),
        ],
        [# tool group 2
            (tool,url),
            (tool,url),
            (tool,url),
        ],
    ]'''

    return False


class TournamentListView(ListView):
    template_name = 'tournament/tournament_list.html'

    model = Tournament
    context_object_name = 'previous_tournaments'

    paginate_by = 1

    queryset = Tournament.public.get_previous()

    def get_context_data(self, **kwargs):
        context = super(TournamentListView, self).get_context_data(**kwargs)
        next_tournaments = Tournament.public.get_next()
        print(next_tournaments)

        tournament_tags = []
        # [[last_places, registraion_full, registration_open],]

        for t in next_tournaments:
            tournament_tags.append([
                (t.max_teams <= t.team_count()+3),
                (t.max_teams <= t.confirmed_team_count()+3),
                t.is_registration_open(),
            ])

        if tournament_tags:
            context.update({
                'next_tournaments': zip(next_tournaments, tournament_tags),
                'detail': False,
            })
        else:
            context.update({
                'next_tournaments': False,
                'detail': False,
            })
        return context


class TournamentDetailView(DetailView):
    template_name = 'tournament/tournament_detail.html'

    model = Tournament
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super(TournamentDetailView, self).get_context_data(**kwargs)
        t = self.get_object()

        c_spots = t.max_teams - t.team_count()
        spots = t.max_teams - t.confirmed_team_count()

        context.update({
            'tabs': get_tabs(self.request.user, t),
            'toolbox': get_toolbox(self.request.user, t),
            'next': t.is_next(),
            'detail': True,
            'tags': [
                (t.max_teams <= t.team_count()+3),
                (t.max_teams <= t.confirmed_team_count()+3),
                t.is_registration_open(),
            ],
            'c_spots': c_spots,
        })

        if c_spots != spots:
            context.update({
                'spots': spots,
            })
        return context
