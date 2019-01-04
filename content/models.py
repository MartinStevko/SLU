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
        verbose_name='nadpis'
    )
    expiration = models.DateTimeField(
        verbose_name='dátum expirácie'
    )

    description = models.TextField(
        verbose_name='popis'
    )
    image = models.ImageField(
        upload_to='news',
        verbose_name='obrázok'
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
        verbose_name='nadpis'
    )
    category = models.CharField(
        max_length=15,
        default='other',
        choices=CATEGORIES,
        verbose_name='kategória'
    )

    description = models.TextField(
        verbose_name='popis'
    )
    image = models.ImageField(
        upload_to='sections',
        verbose_name='obrázok'
    )

    class Meta:
        verbose_name = 'sekcia'
        verbose_name_plural = 'sekcie'

    def __str__(self):
        return '{}'.format(self.title)


class Message(models.Model):
    from_email = models.EmailField(
        verbose_name='odosielateľ'
    )
    send_time = models.DateTimeField(
        default=timezone.now,
        verbose_name='čas poslania'
    )

    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='predmet'
    )
    text = models.TextField(
        verbose_name='správa'
    )

    class Meta:
        verbose_name = 'správa'
        verbose_name_plural = 'správy'

    def __str__(self):
        return '{} - {}'.format(self.subject, self.text)


class OrganizerProfile(models.Model):
    full_name = models.CharField(
        max_length=255,
        verbose_name='celé meno'
    )
    email = models.EmailField(
        verbose_name='e-mail'
    )
    image = models.ImageField(
        upload_to='organizers',
        verbose_name='fotka'
    )

    start_season = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex='^((leto|zima), \d{4}|-)$',
                message='Začiatok aj koniec sezóny musia byť vo formáte leto/zima, YYYY.',
            ),
        ],
        verbose_name='začiatok organizácie'
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
        verbose_name='koniec organizácie'
    )

    class Meta:
        verbose_name = 'profil organizátora'
        verbose_name_plural = 'profily organizátorov'

    def __str__(self):
        return '{}'.format(self.full_name)
