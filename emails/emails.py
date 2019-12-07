from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Template, Context

import random
import string

from emails.models import Template as T_model
from emails.tests import CustomTeam, CustomMatch
from emails.latex import Tex

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

    def __init__(self, recipients, subject, bcc=False):
        if not bcc and type(recipients) == list:
            self.recipients = recipients
            self.bcc_recipients = []
        elif bcc and type(recipients) == list:
            self.recipients = ['slu.central.org@gmail.com']
            self.bcc_recipients = recipients
        elif recipients == 'contact':
            self.recipients = getattr(
                settings,
                'CONTACT_EMAILS',
                ['slu.central.org@gmail.com']
            )
            self.bcc_recipients = []
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

    def registration_open_notification(self, pk):
        plaintext = get_template('emails/registration_open_notification.txt')
        template = get_template('emails/registration_open_notification.html')

        context = {
            'pk': pk,
        }

        self.send_rendered_email(context, plaintext)

    def tournament_activation(self, tournament):
        plaintext = get_template('emails/tournament_activation.txt')

        context = {
            'name': str(tournament),
        }

        self.send_rendered_email(context, plaintext)

    def registration_email(self, team):
        # pre tim ked sa zaregistruju - link na potvrdenie + ze nech upravuju cez ucet
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
        # pre tim, ze ich pozyvame aj info o turnaji
        # ako priloha mozno aj nieco o spirite?
        t = T_model.objects.get(tag='team_invitation')
        plaintext = Template(t.text)
        template = Template(t.html)

        context = Context({
            'team': team,
            'tournament': team.tournament,
        })

        invitation = Tex.generate_invitation(team)
        propositions = Tex.generate_propositions(team.tournament)

        self.send_rendered_email(
            context,
            plaintext,
            html_template=template,
            attachement=[invitation.pdf.path, propositions.pdf.path],
        )

    def last_info_email(self, team, matches):
        plaintext = get_template('emails/last_information.txt')
        template = get_template('emails/last_information.html')

        context = {
            'team': team,
            'matches': matches,
        }

        self.send_rendered_email(context, plaintext, html_template=template)

    def attendee_email(self, team):
        t = T_model.objects.get(tag='attendee_email')
        plaintext = Template(t.text)

        context = Context({
            'team': team,
            'tournament': team.tournament,
        })

        confirmation = Tex.generate_confirmation(team)

        self.send_rendered_email(
            context,
            plaintext,
            attachment=[confirmation.pdf.path]
        )

    def result_email(self, team, place, sotg=False):
        t = T_model.objects.get(tag='result_email')
        plaintext = Template(t.text)
        template = Template(t.html)

        context = Context({
            'team': team,
            'place': place,
        })

        diploma = Tex.generate_diploma(team, sotg=sotg)

        self.send_rendered_email(
            context,
            plaintext,
            template,
            attachment=[diploma.pdf.path]
        )

    def test_mail(self, tag):
        team = CustomTeam()
        match = CustomMatch()

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
        elif tag == 'attendee_email':
            self.attendee_email(team)
        elif tag == 'result_email':
            self.result_email(team, 47)
        else:
            self.send_rendered_email(
                Context({'tag': tag}),
                Template('Nepodarilo sa poslať email s tagom: {{ tag }}.'+\
                    'Pre vyriešenie problému kontaktujte správcu.'),
            )

    def send_rendered_email(self, context, text_template, html_template=None, attachment=None):
        if html_template is not None:
            text_content = text_template.render(context)
            html_content = html_template.render(context)

            email = EmailMultiAlternatives(
                self.subject,
                text_content,
                getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
                self.recipients,
                bcc=self.bcc_recipients,
            )
            email.attach_alternative(html_content, 'text/html')

        else:
            text_content = text_template.render(context)

            email = EmailMessage(
                self.subject,
                text_content,
                getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
                self.recipients,
                bcc=self.bcc_recipients,
                reply_to=['slu.central.org@gmail.com'],
            )

        if attachment is not None:
            for att in attachement:
                email.attach_file(att)

        email.send(fail_silently=False)
