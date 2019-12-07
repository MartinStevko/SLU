from django.shortcuts import render
from django_tex.shortcuts import render_to_pdf


def diplomas_context(tournament, teams):
    template_name = 'latex/diploma.tex'

    context = {
        'all': True,
        'round': 1,
        'season': 2,
        'time': str(tournament.date),
        'place': 'V '+str(tournament.in_city),
        'team': teams,
        'sotg': False,
    }

    if tournament.region == 'F':
        context['round'] = 2

    if tournament.season.season == 'outdoor':
        context['season'] = 1

    return template_name, context, 'diplomy.pdf'


def propositions_context(tournament):
    template_name = 'latex/propositions.tex'

    context = {
        'round': 1,
        'season': 2,
        'qualified': tournament.number_qualified,
        'cap': 1,
        'year': tournament.season.school_year,
        'date': str(tournament.date),
        'reg_date': tournament.signup_deadline,
        'place': tournament.place,
        'arrival_time': tournament.arrival_time,
        'meeting_time': tournament.meeting_time,
        'game_time': tournament.game_time,
        'in_city': tournament.in_city,
        'delegate': tournament.delegate,
        'director': tournament.director,
        'path': 'blue_icon.png',
        'institute': '',
        'orgs': tournament.orgs.all(),
    }

    if tournament.region == 'F':
        context['round'] = 2

    if tournament.season.season == 'outdoor':
        context['season'] = 1
        context['path'] = 'red_icon.png'

    if not tournament.cap:
        context['cap'] += 1

    if tournament.institute:
        context['institute'] = tournament.institute+', '

    return template_name, context, 'propozicie.pdf'
