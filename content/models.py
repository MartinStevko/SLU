from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

from datetime import datetime

CATEGORIES = (
    ('rules', 'Pravidlá'),
    ('ultimate', 'O ultimate'),
    ('other', 'Iné'),
)


class News(models.Model):
    title = models.CharField(
        max_length=127,
        verbose_name='Nadpis'
    )
    expiration = models.DateTimeField(
        verbose_name='Dátum expirácie'
    )

    description = models.TextField(
        verbose_name='Popis'
    )
    image = models.ImageField(
        upload_to='news',
        verbose_name='Obrázok'
    )

    class Meta:
        verbose_name = 'novinka'
        verbose_name_plural = 'novinky'

    def expired(self):
        if self.expiration.replace(tzinfo=None) > datetime.now():
            return False
        else:
            return True

    def __str__(self):
        return '{}'.format(self.title)


class Section(models.Model):
    title = models.CharField(
        max_length=127,
        verbose_name='Nadpis'
    )
    category = models.CharField(
        max_length=15,
        default='other',
        choices=CATEGORIES,
        verbose_name='Kategória'
    )

    description = models.TextField(
        verbose_name='Popis'
    )
    image = models.ImageField(
        upload_to='sections',
        verbose_name='Obrázok'
    )

    class Meta:
        verbose_name = 'sekcia'
        verbose_name_plural = 'sekcie'

    def __str__(self):
        return '{}'.format(self.title)


class Message(models.Model):
    from_email = models.EmailField(
        verbose_name='Odosielateľ'
    )
    send_time = models.DateTimeField(
        default=timezone.now,
        verbose_name='Čas poslania'
    )

    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Predmet'
    )
    text = models.TextField(
        verbose_name='Správa'
    )

    class Meta:
        verbose_name = 'správa'
        verbose_name_plural = 'správy'

    def __str__(self):
        return '{} - {}'.format(self.subject, self.text)


class OrganizerProfile(models.Model):
    full_name = models.CharField(
        max_length=255,
        verbose_name='Celé meno'
    )
    email = models.EmailField(
        verbose_name='E-mail'
    )
    image = models.ImageField(
        upload_to='organizers',
        verbose_name='Fotka'
    )

    start_season = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex='^((leto|zima), \d{4}|-)$',
                message='Začiatok aj koniec sezóny musia byť vo formáte leto/zima, YYYY.',
            ),
        ],
        verbose_name='Začiatok organizácie'
    )
    end_season = models.CharField(
        max_length=15,
        default='-',
        validators=[
            RegexValidator(
                regex='^((leto|zima), \d{4}|-)$',
                message='Začiatok aj koniec sezóny musia byť vo formáte leto/zima, YYYY.',
            ),
        ],
        verbose_name='Koniec organizácie'
    )

    class Meta:
        verbose_name = 'profil organizátora'
        verbose_name_plural = 'profili organizátorov'

    def __str__(self):
        return '{}'.format(self.full_name)
