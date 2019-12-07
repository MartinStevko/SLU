from django.db import models

from froala_editor.fields import FroalaField

TAGS = (
    ('registration_email', 'Registračný e-mail'),
    ('registration_notification', 'Upozornenie o registrácii'),
    ('tournament_full', 'Info o zaradení na čakaciu listinu'),
    ('team_confirmation', 'Info o potvrdení registrácie'),
    ('team_invitation', 'Pozvánka na turnaj'),
    ('attendee_email', 'Potvrdenie účasti'),
    ('result_email', 'Zaslanie diplomu'),
)

DOC_TYPES = (
    ('invitation', 'pozvánka'),
    ('propositions', 'propozície'),
    ('confirmation', 'potvrdenie účasti'),
    ('diploma', 'diplom'),
)


class Template(models.Model):
    tag = models.CharField(
        max_length=31,
        unique=True,
        choices=TAGS,
        help_text='Pri zavolaní tohto tagu sa mail odošle.'
    )
    subject = models.CharField(
        max_length=127,
        verbose_name='názov',
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


class Generic(models.Model):
    name = models.CharField(
        max_length=127,
        verbose_name='meno'
    )
    doc_type = models.CharField(
        max_length=31,
        choices=DOC_TYPES,
        verbose_name='typ'
    )
    pdf = models.FileField(
        upload_to='pdfs/',
        null=True,
        blank=True,
    )
    time_created = models.DateTimeField(
        auto_now=True,
        auto_now_add=True,
        verbose_name='čas vytvorenia',
    )

    class Meta:
        verbose_name = 'generický dokument'
        verbose_name_plural = 'generické dokumenty'

    def __str__(self):
        return "{} - {}".format(self.pk, self.name)
