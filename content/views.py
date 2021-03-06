from django.urls import reverse
from django.core import management
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.generic import TemplateView, View, ListView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.cache import never_cache

from content.models import Section, News, Message, OrganizerProfile
from content.forms import ContactForm
from emails.emails import SendMail


class ContentView(TemplateView):
    title = 'other'
    template_name = 'content/section.html'

    def get_context_data(self, **kwargs):
        context = super(ContentView, self).get_context_data(**kwargs)
        if self.title == 'ultimate':
            context.update({
                'sections': Section.objects.filter(category='ultimate').order_by('order'),
                'title': 'O ultimate',
            })
        elif self.title == 'rules':
            context.update({
                'sections': Section.objects.filter(category='rules').order_by('order'),
                'title': 'Pravidlá',
            })
        else:
            news = []
            for obj in News.objects.all():
                '''
                if obj.expiration.replace(tzinfo=None) > datetime.now():
                    news.append(obj)'''
                if not obj.expired():
                    news.append(obj)

            context.update({
                'sections': Section.objects.filter(category='other').order_by('order'),
                'title': 'Domov',
                'news': news,
            })
        return context


class OrganizersView(ListView):
    template_name = 'content/contact.html'

    model = OrganizerProfile
    context_object_name = 'organizers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context


class ContactFormView(SingleObjectMixin, FormView):
    template_name = 'content/contact.html'
    form_class = ContactForm
    model = Message

    def form_valid(self, form):
        message = form.save(commit=False)
        SendMail(
            'contact',
            message.subject
        ).contact_form(message)
        message.save()

        messages.success(self.request, 'Správa bola úspešne odoslaná!')
        return super(ContactFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('content:contact')


class ContactView(View):

    def get(self, request, *args, **kwargs):
        view = OrganizersView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ContactFormView.as_view()
        return view(request, *args, **kwargs)


class DumpdataView(View):

    @never_cache
    def get(self, *args, **kwargs):
        if self.request.user.is_superuser:
            with open('data.json', 'w') as f:
                management.call_command('dumpdata', indent=4, stdout=f)
            with open('data.json', 'r') as f:
                data = f.read()
            response = HttpResponse(data, content_type='text/json')

        else:
            response = redirect(reverse('content:home'))

        return response
