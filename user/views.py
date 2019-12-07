from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView, RedirectView
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib import messages

from datetime import timedelta, datetime
from random import choice
import string

from emails.emails import SendMail
from .models import *
from .forms import *


class LoginView(FormView):
    template_name = 'user/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('user:login_sent')

    def form_valid(self, form):
        email = form.cleaned_data.get('email', None)
        user = User.objects.get(email=email)

        s = string.ascii_letters + string.digits
        key = ''.join(choice(s) for _ in range(32))

        user.set_password(key)
        user.password_expiration = timezone.now()+timedelta(seconds=60)
        user.save()

        SendMail(
            [email],
            'Prihlásenie '+datetime.now().strftime("%Y-%m-%d %H:%M")
        ).user_login(
            user.pk,
            key,
            self.request.GET.get('next', '/'),
            self.request.META.get('HTTP_HOST', 'https://slu.szf.sk')
        )
        return super().form_valid(form)


class LoginWaitingView(TemplateView):
    template_name = 'user/login_sent.html'


class LoginKeyView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        key = self.kwargs.get('key', None)
        user = get_object_or_404(User, pk=pk)
        if user.password_expiration > timezone.now():
            user = authenticate(email=user.email, password=key)
            if user:
                login(self.request, user)
                user.password_expiration = timezone.now()
                user.save()
                return self.request.GET.get('next', '/')
            else:
                return HttpResponseForbidden()
        else:
            messages.error(self.request, 'Odkaz na prihlásenie už vypršal!')
            return reverse('user:login')
