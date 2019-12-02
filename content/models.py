from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

from datetime import datetime

from tournament.models import Season

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
    published = models.BooleanField(
        default=True,     
        verbose_name='publikované'
    )

    description = models.TextField(
        verbose_name='popis',
        help_text='Text, ktorý sa zobrazí v tele novinky.'
    )
    image = models.ImageField(
        upload_to='news',
        verbose_name='obrázok',
        help_text='Obrázok, ktorý sa zobrazí pri novinke.'
    )

    class Meta:
        verbose_name = 'novinka'
        verbose_name_plural = 'novinky'

        permissions = [
            ('expire_news', 'Can expire news'),
            ('publish_news', 'Can publish news'),
        ]

    def __str__(self):
        return '{}'.format(self.title)

    def expired(self):
        if self.expiration.replace(tzinfo=None) > datetime.now():
            return False
        else:
            return True

    def expire_now(self):
        self.expiration = timezone.now()
        self.save()

    def publish(self):
        self.published = True
        self.save()


class Section(models.Model):
    title = models.CharField(
        max_length=127,
        verbose_name='nadpis'
    )
    category = models.CharField(
        max_length=15,
        default='other',
        choices=CATEGORIES,
        verbose_name='kategória',
        help_text='Kategória v menu, pod ktorou bude sekcia uvedená.'
    )
    published = models.BooleanField(
        default=True,     
        verbose_name='publikované'
    )

    description = models.TextField(
        verbose_name='popis',
        help_text='Text, ktorý sa v sekcii zobrazí.'
    )
    image = models.ImageField(
        upload_to='sections',
        verbose_name='obrázok',
        help_text='Obrázok, ktorý sa v sekcii zobrazí.'
    )

    order = models.SmallIntegerField(
        default=0,
        verbose_name='poradie',
        help_text='Poradové číslo sekcie. Stránka ich zoradí od najmenšieho po najväčšie.'
    )

    class Meta:
        verbose_name = 'sekcia'
        verbose_name_plural = 'sekcie'

        permissions = [
            ('publish_section', 'Can publish '+verbose_name),
        ]

    def __str__(self):
        return '{}'.format(self.title)

    def publish(self):
        self.published = True
        self.save()


class Message(models.Model):
    from_email = models.EmailField(
        verbose_name='odosielateľ'
    )
    send_time = models.DateTimeField(
        default=timezone.now,
        verbose_name='čas poslania'
    )
    archived = models.BooleanField(
        default=False,     
        verbose_name='archivované'
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

        permissions = [
            ('archivate_message', 'Can archivate '+verbose_name),
        ]

    def __str__(self):
        return '{} - {}'.format(self.subject, self.text)

    def archive(self):
        self.archived = True
        self.save()


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
        verbose_name='začiatok organizácie',
        help_text='Vo formáte "leto/zima, YYYY".'
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
        verbose_name='koniec organizácie',
        help_text='Vo formáte "leto/zima, YYYY".'
    )

    class Meta:
        verbose_name = 'profil organizátora'
        verbose_name_plural = 'profily organizátorov'

        permissions = [
            ('end_organizing', 'Can end organizing period'),
        ]

    def __str__(self):
        return '{}'.format(self.full_name)

    def end_now(self):
        s = Season.objects.all()
        s = s[len(s)-1]
        year1, year2 = s.school_year.split('/')
        if s.season == 'outdoor':
            self.end_season = 'leto, ' + year2
        elif s.season == 'indoor':
            self.end_season = 'zima, 0' + year1
        
        self.save()
