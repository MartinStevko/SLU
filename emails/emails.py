from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Template, Context

import random
import string

from emails.models import Template as T_model
from emails.tests import CustomTeam

'''
SendMail(
    ['contact1', 'contact2'],
    'subject'
).method(instance)
'''


def org_list(tournament):
    organizer_emails = []
    for org in tournament.orgs.all():
        organizer_emails.append(org.email)
    for org in tournament.season.orgs.all():
        if org.email not in organizer_emails:
            organizer_emails.append(org.email)

    return organizer_emails


class SendMail:

    def __init__(self, recipients, subject=''):
        if type(recipients) == list:
            self.recipients = recipients
        elif recipients == 'contact':
            self.recipients = getattr(
                settings,
                'CONTACT_EMAILS',
                ['slu.central.org@gmail.com']
            )
        else:
            raise SuspiciousOperation('Príjmateľ správy sa nezhoduje!')

        prefix = getattr(settings, 'EMAIL_SUBJECT_PREFIX', None)
        if prefix:
            self.subject = prefix + ' ' + subject
        else:
            self.subject = subject

    def user_creation(self, user):
        plaintext = get_template('emails/user_creation.txt')
        template = get_template('emails/user_creation.html')

        password = ''

        context = {
            'email': user.email,
        }

        self.send_rendered_email(context, plaintext, html_template=template)

    def user_login(self, pk, key, url_next, host):
        plaintext = get_template('emails/user_login.txt')
        template = get_template('emails/user_login.html')

        context = {
            'pk': pk,
            'key': key,
            'host': host,
            'next': url_next,
        }

        self.send_rendered_email(context, plaintext, html_template=template)

    def contact_form(self, message):
        email = EmailMessage(
            self.subject,
            message.text,
            getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
            self.recipients,
            reply_to=[message.from_email],
        )
        email.send(fail_silently=False)

    def registration_email(self, team):
        # pre tim ked sa zaregistruju - link na potvrdenie a upravu
        t = T_model.objects.get(tag='registration_email')
        plaintext = Template(t.text)
        template = Template(t.html)

        context = Context({
            'team': team,
            'tournament': team.tournament,
            'school': team.school,
        })

        self.send_rendered_email(context, plaintext, html_template=template)

    def registration_notification(self, team, message=None):
        # info pre orgov, ze sa registroval tim
        t = T_model.objects.get(tag='registration_notification')
        plaintext = Template(t.text)
        template = Template(t.html)

        context = Context({
            'team': team,
            'message': message,
            'tournament': team.tournament,
        })

        self.send_rendered_email(context, plaintext, html_template=template)

    def tournament_full(self, team):
        # pre tim, turnaj je plny a su waitlisted
        t = T_model.objects.get(tag='tournament_full')
        plaintext = Template(t.text)
        template = Template(t.html)

        context = Context({
            'team': team,
            'tournament': team.tournament,
        })

        self.send_rendered_email(context, plaintext, html_template=template)

    def team_confirmation(self, team):
        # pre orgov, ze tim potvrdil registraciu
        t = T_model.objects.get(tag='team_confirmation')
        plaintext = Template(t.text)
        template = Template(t.html)

        context = Context({
            'team': team,
            'tournament': team.tournament,
        })

        self.send_rendered_email(context, plaintext, html_template=template)

    def team_invitation(self, team):
        # pre tim, ze ich pozyvame aj info o turnaji a tak
        t = T_model.objects.get(tag='team_invitation')
        plaintext = Template(t.text)
        template = Template(t.html)

        context = Context({
            'team': team,
            'tournament': team.tournament,
        })

        self.send_rendered_email(context, plaintext, html_template=template)

    def test_mail(self, tag):
        team = CustomTeam()

        if tag == 'registration_email':
            self.registration_email(team)
        elif tag == 'registration_notification':
            self.registration_notification(team, message='Skúšobná správa.')
        elif tag == 'tournament_full':
            self.tournament_full(team)
        elif tag == 'team_confirmation':
            self.team_confirmation(team)
        elif tag == 'team_invitation':
            self.team_invitation(team)
        else:
            self.send_rendered_email(
                {'tag': tag},
                Template('Nepodarilo sa posla5 email s tagom: {{ tag }}.\
                    Pre vyriešenie problému kontaktujte správcu.'),
            )

    def send_rendered_email(self, context, text_template, html_template=None):
        if html_template is not None:
            text_content = text_template.render(context)
            html_content = html_template.render(context)

            email = EmailMultiAlternatives(
                self.subject,
                text_content,
                getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
                self.recipients,
            )
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=False)

        else:
            text_content = text_template.render(context)

            email = EmailMessage(
                self.subject,
                text_content,
                getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
                self.recipients,
                reply_to=['slu.central.org@gmail.com'],
            )
            email.send(fail_silently=False)
