from django.shortcuts import render
from datetime import datetime
from django.urls import reverse

from django.views.generic import TemplateView, View, ListView, FormView
from django.views.generic.detail import SingleObjectMixin

from content.models import Section, News, Message, OrganizerProfile
from content.forms import ContactForm

class ContentView(TemplateView):
    title = 'other'
    template_name = 'content/section.html'

    def get_context_data(self, **kwargs):
        context = super(ContentView, self).get_context_data(**kwargs)
        if self.title == 'ultimate':
            context.update({
                'sections': Section.objects.filter(category='ultimate').order_by('-pk'),
                'title': 'O ultimate',
            })
        elif self.title == 'rules':
            context.update({
                'sections': Section.objects.filter(category='rules').order_by('-pk'),
                'title': 'Pravidlá',
            })
        else:
            news = []
            for obj in News.objects.all():
                if obj.expiration.replace(tzinfo=None) > datetime.now():
                    news.append(obj)

            context.update({
                'sections': Section.objects.filter(category='other').order_by('-pk'),
                'title': 'Domov',
                'news': news,
            })
        return context


class OrganizersView(ListView):
    template_name = 'content/contact.html'
    model = OrganizerProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        print(context)
        return context


class ContactFormView(SingleObjectMixin, FormView):
    template_name = 'content/contact.html'
    form_class = ContactForm
    model = Message

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(request, 'Správa bola úspešne odoslaná!')
        return reverse('contact')


class ContactView(View):

    def get(self, request, *args, **kwargs):
        view = OrganizersView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ContactFormView.as_view()
        return view(request, *args, **kwargs)