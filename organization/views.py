from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.sessions.models import Session
from django.conf import settings
from .models import *
from .forms import *

def index(request):
    return HttpResponse("""<h1>
    Registrácia tímov na SLU prebieha
    <a href="http://slu.pythonanywhere.com/prihlasovanie/">TU</a>.
    </h1>""")

def prihlasovanie(request):
    template = 'sign.html'

    if request.method == 'POST':
        teacher_form = TeacherForm(request.POST, prefix='teacher')
        team_form = TeamForm(request.POST, prefix='team')
        gdpr = GDPR(request.POST)
        if settings.SEZONA == 'zima':
            player_form = [
                PlayerForm(request.POST, prefix='1'),
                PlayerForm(request.POST, prefix='2'),
                PlayerForm(request.POST, prefix='3'),
                PlayerForm(request.POST, prefix='4'),
                UnPlayerForm(request.POST, prefix='5'),
                UnPlayerForm(request.POST, prefix='6'),
                UnPlayerForm(request.POST, prefix='7'),
                UnPlayerForm(request.POST, prefix='8'),
            ]
        else:
            player_form = [
                PlayerForm(request.POST, prefix='1'),
                PlayerForm(request.POST, prefix='2'),
                PlayerForm(request.POST, prefix='3'),
                PlayerForm(request.POST, prefix='4'),
                PlayerForm(request.POST, prefix='5'),
                UnPlayerForm(request.POST, prefix='6'),
                UnPlayerForm(request.POST, prefix='7'),
                UnPlayerForm(request.POST, prefix='8'),
                UnPlayerForm(request.POST, prefix='9'),
                UnPlayerForm(request.POST, prefix='10'),
            ]

        v = True
        for pf in player_form:
            if not pf.is_valid():
                v = False

        if gdpr.is_valid() and teacher_form.is_valid() and team_form.is_valid() and v:
            # save to database
            return redirect('admin:index')

        else:
            return render(request, template, {
                'teacher_form':teacher_form,
                'player_form':player_form,
                'team_form':team_form,
                'gdpr':gdpr,
            })

    else:
        teacher_form = TeacherForm(prefix='teacher')
        team_form = TeamForm(prefix='team')
        gdpr = gdpr = GDPR(request.POST)

        if settings.SEZONA == 'zima':
            player_form = [
                PlayerForm(prefix='1'),
                PlayerForm(prefix='2'),
                PlayerForm(prefix='3'),
                PlayerForm(prefix='4'),
                UnPlayerForm(prefix='5'),
                UnPlayerForm(prefix='6'),
                UnPlayerForm(prefix='7'),
                UnPlayerForm(prefix='8'),
            ]
        else:
            player_form = [
                PlayerForm(prefix='1'),
                PlayerForm(prefix='2'),
                PlayerForm(prefix='3'),
                PlayerForm(prefix='4'),
                PlayerForm(prefix='5'),
                UnPlayerForm(prefix='6'),
                UnPlayerForm(prefix='7'),
                UnPlayerForm(prefix='8'),
                UnPlayerForm(prefix='9'),
                UnPlayerForm(prefix='10'),
            ]

        return render(request, template, {
            'teacher_form':teacher_form,
            'player_form':player_form,
            'team_form':team_form,
            'gdpr':gdpr,
        })

def organizacia(request):
    pass
