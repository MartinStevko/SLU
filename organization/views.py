from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import admin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.sessions.models import Session
from .models import *

def index(request):
    return HttpResponse('<h1>Ide to!</h1>')
