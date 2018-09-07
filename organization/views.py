from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.sessions.models import Session
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
        teacher_form = TeacherForm(request.POST)
        player_form = PlayerForm(request.POST)
        team_form = TeamForm(request.POST)
        if teacher_form.is_valid() and player_form.is_valid() and team_form.is_valid():
            teacher_form.save()
            return redirect('admin:index')

        else:
            return render(request, template, {
                'teacher_form':teacher_form,
                'player_form':player_form,
                'team_form':team_form,
            })

    else:
        teacher_form = TeacherForm()
        player_form = PlayerForm()
        team_form = TeamForm()
        return render(request, template, {
            'teacher_form':teacher_form,
            'player_form':player_form,
            'team_form':team_form,
        })

def organizacia(request):
    pass
