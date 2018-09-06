from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import admin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.sessions.models import Session
from .models import *

def index(request):
    return HttpResponse("""<h1>
    Registrácia tímov na SLU prebieha
    <a href="http://slu.pythonanywhere.com/prihlasovanie/">TU</a>.
    </h1>""")

def prihlasovanie(request):
    pass

def organizacia(request):
    pass
