from django.shortcuts import render
from django.urls import reverse
from django.http import Http404
from django.core import serializers
from django.http import JsonResponse
from django.contrib import messages

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.list import BaseListView
from django.views.generic.edit import DeleteView

import datetime

from app.utils import decode, get_key
from tournament.models import *
from .forms import *
# from todoes.models import Todo


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
                reverse('registration:create', kwargs={'pk': t.pk}),
                False
            ))
        elif t.max_teams > t.confirmed_team_count():
            tabs.append((
                'Registrácia',
                reverse('registration:create', kwargs={'pk': t.pk}),
                'Posledné miesta'
            ))
        else:
            pass

    # Schedule view
    if len(Match.objects.filter(tournament=t.id)) > 0:
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
    if t.state == 'results':
        tabs.append((
            'Výsledky',
            reverse('tournament:results', kwargs={'pk': t.pk}),
            False
        ))

    # Gallery
    if t.state == 'results':
        if len(Photo.objects.filter(tournament=1)) > 1:
            tabs.append((
                'Galéria',
                reverse('tournament:gallery', kwargs={'pk': t.pk}),
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

                tab = (
                    name_str,
                    reverse('registration:change', kwargs={'pk': team.pk}),
                    False
                )
                if tab not in tabs:
                    tabs.append(tab)

    if request.user.is_authenticated:
        teachers = Teacher.objects.filter(email=request.user.email)
        for team in Team.objects.filter(teacher__in=teachers):
            if team.tournament.date < datetime.datetime.now().date():
                continue
            else:
                if len(team.get_name()) > 20:
                    name_str = team.get_name()[:17] + '...'
                else:
                    name_str = team.get_name()

                tab = (
                    name_str,
                    reverse('registration:change', kwargs={'pk': team.pk}),
                    False
                )
                if tab not in tabs:
                    tabs.append(tab)

        for team in Team.objects.filter(extra_email=request.user.email):
            if team.tournament.date < datetime.datetime.now().date():
                continue
            else:
                if len(team.get_name()) > 20:
                    name_str = team.get_name()[:17] + '...'
                else:
                    name_str = team.get_name()

                tab = (
                    name_str,
                    reverse('registration:change', kwargs={'pk': team.pk}),
                    False
                )
                if tab not in tabs:
                    tabs.append(tab)

    return tabs


def get_toolbox(user, obj):
    if user.is_staff:
        toolgroups = []

        # Basic toolgroup
        toolgroups.append([])
        if user.has_perm('tournament.change_tournament'):

            # Tournament administration site
            toolgroups[-1].append((
                'Spravovať turnaj',
                reverse('admin:tournament_tournament_change', args=(obj.id,))
            ))
        '''if user in obj.orgs and Todo.objects.filter(tournament=obj):

            # Organizers checklist
            toolgroups[-1].append((
                'Zoznam úloh',
                reverse('todoes:tournament_todoes', kwargs=({
                    'pk': obj.pk,
                }))
            ))'''

        toolgroups.append([])
        # team management - add

        toolbox = []
        for group in toolgroups:
            if group:
                toolbox.append(group)
        return toolbox

    else:

        return False


class JSONResponseMixin:

    def render_to_json_response(self, context, **response_kwargs):
        response = JsonResponse(
            self.get_data(context),
            **response_kwargs,
            safe=False
        )

        return response

    def get_data(self, context):
        data = context['points']

        return list(data)


class TournamentIsPublicMixin(object):

    def get_context_data(self, **kwargs):
        context = super(TournamentIsPublicMixin, self).get_context_data(**kwargs)
        t = self.get_object()

        if t.state == 'not_public' and not self.request.user.is_staff:
            raise Http404('Hľadaný turnaj nebol zverejnený')
        else:
            return context


class HavePlayerStatsMixin(object):

    def get_context_data(self, **kwargs):
        context = super(TournamentIsPublicMixin, self).get_context_data(**kwargs)
        t = self.get_object()

        if t.player_stats:
            return context
        else:
            raise Http404('Tento turnaj nemá hráčske štatistiky')


class TabsViewMixin(object):

    def get_context_data(self, **kwargs):
        context = super(TabsViewMixin, self).get_context_data(**kwargs)
        t = self.get_object()

        context.update({
            'tabs': get_tabs(self.request, t),
            'toolbox': get_toolbox(self.request.user, t),
        })

        return context


class TournamentListView(ListView):
    template_name = 'tournament/tournament_list.html'

    model = Tournament
    context_object_name = 'previous_tournaments'

    paginate_by = 4

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


class TournamentDetailView(TabsViewMixin, TournamentIsPublicMixin, DetailView):
    template_name = 'tournament/tournament_detail.html'

    model = Tournament
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super(TournamentDetailView, self).get_context_data(**kwargs)
        t = self.get_object()

        c_spots = t.max_teams - t.team_count()
        spots = t.max_teams - t.confirmed_team_count()

        context.update({
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


class JSONPointListView(JSONResponseMixin, BaseListView):
    template_name = 'tournament/tournament_list.html'

    model = Point
    context_object_name = 'points'

    def get_queryset(self):
        m_pk = self.request.GET.get('match', None)
        try:
            m = Match.objects.get(pk=m_pk)
        except(Match.DoesNotExist):
            raise Http404('Tento zápas neexistuje')

        if m:
            queryset = []

            points = Point.objects.filter(match=m)

            for i in range(len(points)):
                p = points[i]
                '''p_dict = p.values(
                    'time',
                    'score__first_name',
                    'score__last_name',
                    'assist__first_name',
                    'assist__last_name',
                )'''
                p_dict = {}
                p_dict['time'] = p.time
                if p.score:
                    p_dict['score__first_name'] = p.score.first_name
                    p_dict['score__last_name'] = p.score.last_name
                else:
                    p_dict['score__first_name'] = 'null'
                    p_dict['score__last_name'] = 'null'
                if p.assist:
                    p_dict['assist__first_name'] = p.assist.first_name
                    p_dict['assist__last_name'] = p.assist.last_name
                else:
                    p_dict['assist__first_name'] = 'null'
                    p_dict['assist__last_name'] = 'null'

                if p.score in m.home_team.players.all():
                    p_dict['score__team__name'] = m.home_team.get_name()

                if p.score in m.host_team.players.all():
                    p_dict['score__team__name'] = m.host_team.get_name()

                queryset.append(p_dict)

        else:
            queryset = False

        return queryset


    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class TournamentMatchesView(TournamentIsPublicMixin, TabsViewMixin, DetailView):
    template_name = 'tournament/match_list.html'

    model = Tournament
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super(TournamentMatchesView, self).get_context_data(**kwargs)
        t = self.get_object()

        matches = Match.objects.filter(tournament=t)
        scores = []

        for m in matches:
            points = Point.objects.filter(match=m)

            home_players = m.home_team.players.all()
            host_players = m.host_team.players.all()

            home_score = 0
            host_score = 0
            for p in points:
                if p.score in home_players:
                    home_score += 1
                if p.score in host_players:
                    host_score += 1

            scores.append([home_score, host_score])

        context.update({
            'matches': zip(matches, scores),
        })

        return context


class PointDeleteView(UserPassesTestMixin, DeleteView):

    model = Point

    def get_success_url(self):
        pk = self.kwargs.get('match', None)


        return reverse('tournament:match_detail', args=(pk,))

    def test_func(self):
        return self.request.user.is_staff


class MatchDetailView(FormView):
    template_name = 'tournament/match_detail.html'

    form_class = ScoringForm
    model = Point

    def form_valid(self, form):
        pk = self.kwargs.get('pk', None)
        m = Match.objects.get(pk=pk)

        score = form.cleaned_data.get('score', None)
        assist = form.cleaned_data.get('assist', None)

        if m.tournament.player_stats:
            if 'add_to_home_team' in self.request.POST:
                if score not in m.home_team.players.all():
                    messages.error(
                        self.request,
                        'Hráč {} nie je v tíme {}, ktorému \
                        pridávaš bod!'.format(score, m.home_team)
                    )

                    return super(MatchDetailView, self).form_invalid(form)

                if assist and assist not in m.home_team.players.all():
                    messages.error(
                        self.request,
                        'Hráč {} nie je v tíme {}, ktorému \
                        pridávaš bod!'.format(assist, m.home_team)
                    )

                    return super(MatchDetailView, self).form_invalid(form)

            if 'add_to_host_team' in self.request.POST:
                if score not in m.host_team.players.all():
                    messages.error(
                        self.request,
                        'Hráč {} nie je v tíme {}, ktorému \
                        pridávaš bod!'.format(score, m.host_team)
                    )

                    return super(MatchDetailView, self).form_invalid(form)

                if assist and assist not in m.host_team.players.all():
                    messages.error(
                        self.request,
                        'Hráč {} nie je v tíme {}, ktorému \
                        pridávaš bod!'.format(assist, m.host_team)
                    )

                    return super(MatchDetailView, self).form_invalid(form)

        point = form.save(commit=False)
        point.match = m

        if not m.tournament.player_stats:
            if 'add_to_home_team' in self.request.POST:
                try:
                    point.score = m.home_team.players.all()[0]
                except(IndexError):
                    messages.error(
                        self.request,
                        'Tím {} nemá ani jedného hráča. Najprv nejakého \
                        pridaj.'.format(m.home_team)
                    )

                    return super(MatchDetailView, self).form_invalid(form)

            if 'add_to_host_team' in self.request.POST:
                try:
                    point.score = m.host_team.players.all()[0]
                except(IndexError):
                    messages.error(
                        self.request,
                        'Tím {} nemá ani jedného hráča. Najprv nejakého \
                        pridaj.'.format(m.host_team)
                    )

                    return super(MatchDetailView, self).form_invalid(form)

        point.save()

        if 'add_to_home_team' in self.request.POST:
            messages.success(
                self.request,
                'Bol pridaný bod pre tím {}.'.format(point.match.home_team.name)
            )
        elif 'add_to+host_team' in self.request.POST:
            messages.success(
                self.request,
                'Bol pridaný bod pre tím {}.'.format(point.match.host_team.name)
            )

        return super(MatchDetailView, self).form_valid(form)

    def get_success_url(self):
        pk = self.kwargs.get('pk', None)
        return reverse('tournament:match_detail', args=(pk,))

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk', None)
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        try:
            m = Match.objects.get(pk=pk)
        except(Match.DoesNotExist):
            raise Http404('Hľadaný zápas neexistuje')

        if m.tournament.state == 'not_public' and not self.request.user.is_staff:
            raise Http404('Hľadaný turnaj nebol zverejnený')

        related_players = Player.objects.filter(team__in=[m.home_team, m.host_team])
        f_fields = context['form'].fields
        f_fields['score'].queryset = related_players
        f_fields['assist'].queryset = related_players

        points = Point.objects.filter(match=m)

        score = [0, 0]
        teams = []
        for p in points:
            if p.score in m.home_team.players.all():
                score[0] += 1
                teams.append(m.home_team)

            if p.score in m.host_team.players.all():
                score[1] += 1
                teams.append(m.host_team)

        context.update({
            'match': m,
            'tournament': m.tournament,
            'points': zip(points, teams),
            'score': score,
        })

        toolbox = get_toolbox(self.request.user, m.tournament)
        toolbox[0].append((
            'Upraviť zápas',
            reverse('admin:tournament_match_change', args=(m.id,))
        ))

        context.update({
            'tabs': get_tabs(self.request, m.tournament),
            'toolbox': toolbox,
        })

        return context


class PlayerStatsView(HavePlayerStatsMixin, TournamentIsPublicMixin, TabsViewMixin, DetailView):
    template_name = 'tournament/player_stats.html'

    model = Tournament
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super(PlayerStatsView, self).get_context_data(**kwargs)
        t = self.get_object()

        stats = []
        for team in Team.objects.filter(tournament=t):
            for player in team.players.all():
                s = len(Point.objects.filter(score=player))
                a = len(Point.objects.filter(assist=player))

                stats.append([player, [s, a, s+a]])

        stats.sort(key=lambda x: -x[1][2])

        context.update({
            'next': t.is_next(),
            'detail': True,
            'stats': stats[len(stats)-25:],
        })

        return context


class TournamentResultsView(TournamentIsPublicMixin, TabsViewMixin, DetailView):
    template_name = 'tournament/results.html'

    model = Tournament
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super(TournamentResultsView, self).get_context_data(**kwargs)
        t = self.get_object()

        if t.state != 'results':
            raise Http404('Výsledky pre tento turnaj ešte neexistujú.')

        context.update({
            'next': t.is_next(),
            'detail': True,
            'results': Result.objects.filter(tournament=t).order_by('place'),
        })

        return context


class TournamentGalleryView(TournamentIsPublicMixin, TabsViewMixin, DetailView):
    template_name = 'tournament/gallery.html'

    model = Tournament
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super(TournamentGalleryView, self).get_context_data(**kwargs)
        t = self.get_object()

        if t.state != 'results':
            raise Http404('Galéria pre tento turnaj ešte neexistuje.')

        context.update({
            'photos': Photo.objects.filter(tournament=t),
        })

        return context
