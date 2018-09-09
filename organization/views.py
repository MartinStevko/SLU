from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.formsets import formset_factory

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
    if settings.SEZONA == 'zima':
        PlayerFormSet = formset_factory(PlayerForm, min_num=4, validate_min=True, extra=4)
    else:
        PlayerFormSet = formset_factory(PlayerForm, min_num=5, validate_min=True, extra=5)

    if request.method == 'POST':
        teacher_form = TeacherForm(request.POST, prefix='teacher')
        team_form = TeamForm(request.POST, prefix='team')
        gdpr = GDPR(request.POST)
        formset = PlayerFormSet(request.POST)

        if all([gdpr.is_valid(), team_form.is_valid(), teacher_form.is_valid(), formset.is_valid()]):
            try:
                suhlas_ou = request.POST['suhlas_ou']
                suhlas_mf = request.POST['suhlas_mf']
            except:
                suhlas_ou = False
                suhlas_mf = False

            if suhlas_ou and suhlas_mf:
                ucitel = teacher_form.save(commit=False)
                ucitelia = Teacher.objects.all()
                print('Ukladanie ' + ucitel.meno)
                ucitel.save()
                tim = team_form.save(commit=False)
                tim.ucitel = ucitel
                print('Ukladanie ' + tim.meno)
                tim.save()
                for form in formset:
                    if form.is_valid():
                        hrac = form.save(commit=False)
                        hrac.tim = tim
                        if hrac.meno != '':
                            print('Ukladanie ' + hrac.meno)
                            hrac.save()
                return HttpResponse('<h1 style="text-align: center; margin-top: 50px;">Registrácia bola úspešná!</h1>')
            else:
                return HttpResponse('<h1 style="text-align: center; margin-top: 50px;">Z dôvodu neudelenia súhlasu nebolo možné vás zaregistrovať.</h1>')

        else:
            return render(request, template, {
                'teacher_form':teacher_form,
                'player_form':formset,
                'team_form':team_form,
                'gdpr':gdpr,
            })

    else:
        teacher_form = TeacherForm(prefix='teacher')
        team_form = TeamForm(prefix='team')
        gdpr = gdpr = GDPR(request.POST)
        formset = PlayerFormSet()

        return render(request, template, {
            'teacher_form':teacher_form,
            'player_form':formset,
            'team_form':team_form,
            'gdpr':gdpr,
        })

def organizacia(request):
    pass
