from django_tex.core import compile_template_to_pdf
from django.core.files.base import ContentFile

from emails.models import Generic


def test():
    template = 'latex/confirmation.tex'
    context = {
        'players': ['']*10,
        'teacher': 'Meno Ucitela',
        'school': 'Nazov skoly',
        'place': 'SOS Ostrovskeho 1',
        'time': '15.12.2019',
        'round': 1,
        'season': 2,
        'num': 2,
    }
    pdf = compile_template_to_pdf(template, context)
    filename = 'test.pdf'

    obj = Generic.objects.create(slug='test')
    obj.pdf.save(filename, ContentFile(pdf))

    email = EmailMessage(
        'Test LaTeX-u',
        'Ahoj, toto je testovacia sprava.',
        getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
        ['mstevko10@gmail.com'],
    )

    email.attach_file(obj.pdf.path)

    email.send(fail_silently=False)


class Tex:
    @staticmethod
    def generate_invitation(team):
        template = 'latex/invitation.tex'

        time = str(team.tournament.date)
        time += ' od '+team.tournament.arrival_time.strftime("%H:%M")
        time += ' do '+team.tournament.end_time.strftime("%H:%M")
        context = {
            'team': str(team),
            'school': str(team.school),
            'place': 'v '+team.tournament.in_city,
            'time': time,
            'round': 0,
            'season': 0,
            'num': int(team.tournament.season.school_year.split('/')[0])-2018,
        }
        if team.tournament.region == 'F':
            context['round'] = 1
        if team.tournament.season.season == 'outdoor':
            context['season'] = 1
            context['num'] += 1
        pdf = compile_template_to_pdf(template, context)

        filename = 'invitation.pdf'
        obj = Generic.objects.create(
            name='Pozvánka - {}'.format(str(team)),
            doc_type='invitation',
        )
        obj.pdf.save(filename, ContentFile(pdf))

        return obj

    @staticmethod
    def generate_confirmation(team):
        template = 'latex/confirmation.tex'

        players = ['']*10
        i = 0
        for p in team.players.all():
            if i<10:
                players[i] = str(p)
                i += 1
            else:
                break

        context = {
            'players': players,
            'teacher': str(team.teacher),
            'school': str(team.school),
            'place': team.tournament.place,
            'time': str(team.tournament.date),
            'round': 1,
            'season': 2,
            'num': int(team.tournament.season.school_year.split('/')[0])-2018,
        }
        if team.tournament.region == 'F':
            context['round'] = 2
        if team.tournament.season.season == 'outdoor':
            context['season'] = 1
            context['num'] += 1
        pdf = compile_template_to_pdf(template, context)

        filename = 'confirmation.pdf'
        obj = Generic.objects.create(
            name='Potvrdenka - {}'.format(str(team)),
            doc_type='confirmation',
        )
        obj.pdf.save(filename, ContentFile(pdf))

        return obj

    @staticmethod
    def generate_propositions(tournament):
        template = 'latex/propositions.tex'

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
            'orgs': tournament.orgs,
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
        pdf = compile_template_to_pdf(template, context)

        filename = 'propositions.pdf'
        obj = Generic.objects.create(
            name='Propozície - {}'.format(str(tournament)),
            doc_type='propositions',
        )
        obj.pdf.save(filename, ContentFile(pdf))

        return obj

    @staticmethod
    def generate_diploma(team, sotg=False):
        template = 'latex/diploma.tex'

        context = {
            'all': False,
            'round': 1,
            'season': 2,
            'time': str(team.tournament.date),
            'place': 'V '+str(team.tournament.in_city),
            'team': str(team),
            'sotg': sotg,
        }
        if team.tournament.region == 'F':
            context['round'] = 2
        if team.tournament.season.season == 'outdoor':
            context['season'] = 1
        pdf = compile_template_to_pdf(template, context)

        filename = 'diploma.pdf'
        obj = Generic.objects.create(
            name='Diplom - {}'.format(str(team)),
            doc_type='diploma',
        )
        obj.pdf.save(filename, ContentFile(pdf))

        return obj
