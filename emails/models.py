from django.db import models

from froala_editor.fields import FroalaField

TAGS = (
    ('email_name', 'Meno emailu'),
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
