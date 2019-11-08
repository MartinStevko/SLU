from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import PermissionDenied

from django.forms import modelformset_factory
from django.views.generic import FormView, DetailView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormMixin

import time

from app.utils import encode, decode, get_key
from app.emails import SendMail, org_list
from registration.models import *
from tournament.models import Tournament, Team
from .forms import *


def registration_redirect(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    key = get_key()
    request.session['registration_data'] = encode(key, str(pk))

    return redirect('registration:create_school')


class SchoolRegistrationView(FormView):
    template_name = 'registration/registration.html'

    form_class = SchoolForm
    model = School

    def form_valid(self, form):
        school = form.cleaned_data.get('choose_school', None)
        if not school:
            school = form.save()

        data = self.request.session.get('registration_data', None)
        if not data:
            raise PermissionDenied('Registrácia neplatná, chcete nás hacknúť?!')
        else:
            key = get_key()
            data = decode(key, data) + '-' + str(school.pk)
            self.request.session['registration_data'] = encode(key, data)

        messages.success(self.request, 'Škola bola úspešne pridaná. \
        Pre dokončenie registrácie pokračujte vyplnením údajov o učiteľovi a tíme.')
        return super(SchoolRegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('registration:create_teacher')


class TeacherRegistrationView(FormView):
    template_name = 'registration/registration.html'

    form_class = TeacherForm
    model = Teacher

    def form_valid(self, form):
        data = self.request.session.get('registration_data', None)
        if not data:
            raise PermissionDenied('Registrácia neplatná, chcete nás hacknúť?!')
        else:
            key = get_key()
            data = [int(x) for x in decode(key, data).split('-')]

        teacher = form.save(commit=False)
        teacher.school = School.objects.get(pk=data[1])
        teacher.save()

        data.append(teacher.pk)
        temp = ''
        for pk in data:
            temp += '-' + str(pk)
        self.request.session['registration_data'] = encode(key, temp[1:])

        messages.success(self.request, 'Učiteľ bol úspešne pridaný. \
        Pre dokončenie registrácie pokračujte vyplnením údajov o tíme.')
        return super(TeacherRegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('registration:create_team')


class TeamRegistrationView(FormView):
    template_name = 'registration/registration.html'

    form_class = TeamForm
    model = Team

    def form_valid(self, form):
        team = form.save(commit=False)

        data = self.request.session.get('registration_data', None)
        if not data:
            raise PermissionDenied('Registrácia neplatná, chcete nás hacknúť?!')
        else:
            key = get_key()
            data = [int(x) for x in decode(key, data).split('-')]

        try:
            team.tournament = Tournament.objects.get(pk=data[0])
            team.school = School.objects.get(pk=data[1])
            team.teacher = Teacher.objects.get(pk=data[2])
            team.name = team.school.name
        except(Tournament.DoesNotExist, School.DoesNotExist, Teacher.DoesNotExist):
            raise PermissionDenied('Registrácia neplatná, chcete nás hacknúť?!')

        message = form.cleaned_data.get('message', '')

        SendMail(
            org_list(team.tournament),
            'Registrácia - '+str(team.school)
        ).registration_notification(team, message)
        SendMail(
            team.get_emails(),
            'Potvrdenie registrácie'
        ).registration_email(team)

        team.save()

        messages.success(self.request, 'Váš tím je úspešne zaregistrovaný \
        na tento turnaj. Pre potvrdenie registrácie prosím kliknite na odkaz \
        v emaily, ktorý sme vám práve poslali. Po potvrdení registrácie \
        dostanete email s pozvánkou.')
        return super(TeamRegistrationView, self).form_valid(form)

    def get_success_url(self):
        data = self.request.session.get('registration_data', None)
        if not data:
            raise PermissionDenied('Registrácia neplatná, chcete nás hacknúť?!')
        else:
            key = get_key()
            data = [int(x) for x in decode(key, data).split('-')]

            del self.request.session['registration_data']

        return reverse('tournament:detail', args=(data[0],))


def confirmation_redirect(request, identifier):
    try:
        team = Team.objects.get(identifier=identifier)
    except(Team.DoesNotExist):
        time.sleep(3)
        messages.error(self.request, 'Hľadaný tím nebol nájdený. \
        Snažíte sa nás hacknúť?!')
        return redirect('content:home')

    t = team.tournament
    if team.status == 'registered':
        team.confirmed = True
        if len(Team.objects.filter(tournament=t)) >= t.max_teams:
            SendMail(
                team.get_emails()+org_list(t),
                'Registráciu nebolo možné potvrdiť'
            ).tournament_full(team)
            team.status = 'waitlisted'
            messages.warn(request, 'Vaša registrácia je potvrdená, \
            avšak na turnaji zatiaľ nie ste očakávaní, keďže voľné \
            miesta na turnaji sa minuli. Ak nejaký z tímov odmietne \
            účasť, budeme vás kontaktovať.')
        else:
            SendMail(
                team.get_emails(),
                'Registrácia dokončená'
            ).team_invitation(team)
            SendMail(
                org_list(t),
                'Potvrdenie účasti - '+str(team.school)
            ).team_confirmation(team)
            team.status = 'invited'
            messages.success(request, 'Vaša registrácia je potvrdená, \
            tešíme sa na vás na turnaji!')

        team.save()

    key = get_key()
    registered = request.session.get('team_list', None)
    if not registered or type(registered) != list:
        registered = []

    registered.append(encode(key, identifier))
    request.session['team_list'] = registered

    return redirect('registration:change', pk=team.pk)


class ChangeTeamView(FormMixin, DetailView):
    template_name = 'registration/player_list.html'

    model = Team
    form_class = PlayerForm

    def is_identifier_valid(self, team):
        authorizied = self.request.session.get('team_list', None)
        key = get_key()

        if encode(key, str(team.identifier)) in authorizied:
            return True
        else:
            time.sleep(3)
            raise PermissionDenied('Tento tím nemáte oprávnenie \
            meniť. Snažíte sa nás hacknúť?!')

    def post(self, request, *args, **kwargs):
        team = self.get_object()
        if not self.is_identifier_valid(team):
            return HttpResponseForbidden()

        total = int(request.POST['form-TOTAL_FORMS'])
        initial = int(request.POST['form-INITIAL_FORMS'])
        f_max = int(request.POST['form-MAX_NUM_FORMS'])
        players = []
        for i in range(total):
            field = 'form-' + str(i) + '-'
            players.append([
                request.POST[field+'first_name'],
                request.POST[field+'last_name'],
                request.POST[field+'sex'],
                request.POST[field+'id']
            ])

        changes = []
        errors = []
        for p in players:
            if p[3]:
                player = Player.objects.get(pk=int(p[3]))
            else:
                player = Player(
                    school=team.school,
                )
            
            if (p[0] and len(p[0]) > 2 and len(p[0]) < 255 and
                p[1] and len(p[1]) > 2 and len(p[1]) < 255 and
                p[2] and p[2] in ['male', 'female']):

                player.first_name = p[0]
                player.last_name = p[1]
                player.sex = p[2]

                player.save()
                team.players.add(player)

                changes.append(str(player))
            
            else:
                if not p[0] and not p[1] and not p[2]:
                    pass
                else:
                    errors.append(
                        'Hráča {} {} nebolo možné registrovať, pretože \
                        nemá správne vyplnené údaje. Meno aj priezvisko \
                        musia byť vyplnené a ako pohlavie musíte vybrať \
                        jednu z ponúknutých možností.'.format(p[0], p[1])
                    )

        s = 'Hráči '
        for p in changes:
            s += p + ', '
        s = s[:len(s)-2]
        s += ' boli úspešne uložení.'
        messages.success(request, s)

        for e in errors:
            messages.error(request, e)

        return redirect('registration:change', pk=team.pk)

    def get_context_data(self, **kwargs):
        team = self.get_object()

        if self.is_identifier_valid(team):
            context = super(ChangeTeamView, self).get_context_data(**kwargs)

            if team.tournament.season.season == 'indoor':
                x = 8
            else:
                x = 10

            context.update({
                'form': modelformset_factory(
                    Player,
                    form=PlayerForm,
                    max_num=x,
                    extra=x
                )(queryset=team.players.all())
            })

            return context
