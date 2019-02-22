from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def org_list(tournament):
    organizer_emails = []
    for org in tournament.orgs.all():
        organizer_emails.append(org.email)
    for org in tournament.season.orgs.all():
        if org.email not in organizer_emails:
            organizer_emails.append(org.email)

    return organizer_emails


class SendMail:

    def __init__(self, recipients, subject):
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

        # priklad pouzitia:
        # plaintext = get_template('email.txt')
        # htmly = get_template('email.html')
        # d = Context({ 'username': username })

        # self.send_rendered_email(d, plaintext, htmly)
        pass

    def registration_notification(self, team, message=None):
        # info pre orgov, ze sa registroval tim
        pass

    def tournament_full(self, team):
        # pre tim, turnaj je plny a su waitlisted
        pass

    def team_confirmation(self, team):
        # pre orgov, ze tim potvrdil registraciu
        pass

    def team_invitation(self, team):
        # pre tim, ze ich pozyvame aj info o turnaji a tak
        pass

    def send_rendered_email(self, context, text_template, html_template=None):
        if html_template:
            text_content = text_template.render(context)
            html_content = html_template.render(context)
            '''
            email = EmailMultiAlternatives(
                self.subject,
                text_content,
                getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
                self.recipients,
            )
            email.attach_alternative(html_content, 'text/html')

            # or

            email = EmailMultiAlternatives(
                self.subject,
                html_content,
                getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
                self.recipients,
            )
            email.content_subtype = 'html'
            '''
            email.send(fail_silently=False)

        else:
            text_content = text_template.render(context)

            email = EmailMessage(
                self.subject,
                text_content,
                getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
                self.recipients,
            )
            email.send(fail_silently=False)
