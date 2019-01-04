from django.conf import settings
from django.core.exceptions import SuspiciousOperation


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
            self.recipients = [getattr(
                settings,
                'CONTACT_EMAIL',
                'slu.central.org@gmail.com'
            )]
        else:
            raise SuspiciousOperation('Príjmateľ správy sa nezhoduje!')

        self.subject = subject

    def contact_form(self, message):
        # pre orgov, ked niekto submitne odpoved
        pass

    def registration_email(self, team):
        # pre tim ked sa zaregistruju - link na potvrdenie a upravu
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
