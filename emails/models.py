from django.db import models

from froala_editor.fields import FroalaField

TAGS = (
    ('registration_email', 'Registračný e-mail'),
    ('registration_notification', 'Upozornenie o registrácii'),
    ('tournament_full', 'Info o zaradení na čakaciu listinu'),
    ('team_confirmation', 'Info o potvrdení registrácie'),
    ('team_invitation', 'Pozvánka na turnaj'),
    ('attendee_email', 'Potvrdenie účasti'),
)


class Template(models.Model):
    tag = models.CharField(
        max_length=15,
        unique=True,
        choices=TAGS,
        help_text='Pri zavolaní tohto tagu sa mail odošle.'
    )
    subject = models.CharField(
        max_length=127,
        verbose_name='predmet',
    )
    text = models.TextField()
    html = FroalaField(
        blank=True,
        help_text='Môže ostať prázdne, ale ak je vyplnené, pošle sa ako primárny obsah.'
    )

    class Meta:
        verbose_name = 'šablóna'
        verbose_name_plural = 'šablóny'

    def __str__(self):
        return str(self.subject)
