from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, TemplateView

from app.utils import decode, get_key
from tournament.models import Tournament, Match, Result, Team


def get_tabs(request, t):
    # Tournament detail view
    tabs = [(
        'Turnaj',
        reverse('tournament:detail', kwargs={'pk': t.pk}),
        False
    )]

    # Registration
    if t.is_registration_open():
        if t.max_teams > t.team_count()+3:
            tabs.append((
                'Registrácia',
                reverse('registration:create'),
                False
            ))
        elif t.max_teams > t.confirmed_team_count():
            tabs.append((
                'Registrácia',
                reverse('registration:create'),
                'Posledné miesta'
            ))
        else:
            pass

    # Schedule view
    if len(Match.objects.filter(tournament=t.id)) >= 5:
        tabs.append((
            'Rozpis zápasov',
            reverse('tournament:match_list', kwargs={'pk': t.pk}),
            False
        ))

    # Player stats
    if t.player_stats and (t.state == 'active' or t.state == 'results'):
        tabs.append((
            'Štatistiky hráčov',
            reverse('tournament:player_stats', kwargs={'pk': t.pk}),
            False
        ))

    # Results
    if len(Result.objects.filter(tournament=t.id)) >= 1:
        tabs.append((
            'Výsledky',
            reverse('tournament:results', kwargs={'pk': t.pk}),
            False
        ))

    # My team
    team_cookies = request.session.get('team_list', False)
    if team_cookies:
        for c in team_cookies:
            try:
                i = decode(get_key(), c)
            except:
                i = ''
            try:
                team = Team.objects.get(identifier=i)
            except(Team.DoesNotExist):
                pass
            else:
                if len(team.get_name()) > 20:
                    name_str = team.get_name()[:17] + '...'
                else:
                    name_str = team.get_name()

                tabs.append((
                    name_str,
                    reverse('registration:change', kwargs={'pk': team.pk}),
                    False
                ))

    return tabs


def get_toolbox(user, obj):
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
    if user.is_staff:
        toolgroups = []

        toolgroups.append([])
        if user.has_perm('tournament.change_tournament'):
            toolgroups[-1].append((
                'Spravovať turnaj',
                reverse('admin:tournament_tournament_change', args=(obj.id,))
            ))

        toolgroups.append([])
        # team management

        toolbox = []
        for group in toolgroups:
            if group:
                toolbox.append(group)
        return toolbox

    else:

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
            'tabs': get_tabs(self.request, t),
            'toolbox': get_toolbox(self.request.user, t),
            'next': t.is_next(),
            'detail': True,
            'tags': [
                (t.max_teams <= t.team_count()+3),
                (t.max_teams <= t.confirmed_team_count()),
                t.is_registration_open(),
            ],
            'c_spots': c_spots,
        })

        if c_spots != spots:
            context.update({
                'spots': spots,
            })
        return context

# self.kwargs.get('id', None)
class TournamentMatchesView(ListView):
    pass


# dodat aj spatny link
class MatchDetailView(DetailView):
    pass


class PlayerStatsView(TemplateView):
    pass


class TournamentResultsView(TemplateView):
    pass
