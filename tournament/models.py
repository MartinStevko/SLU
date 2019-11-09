from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.db import models
from django.utils import timezone
from django.core.validators import (
    RegexValidator,
    MaxValueValidator,
    MinValueValidator
)

import os
from uuid import uuid4
import datetime

from django.contrib.auth.models import User
from registration.models import School, Teacher, Player

SEASONS = (
    ('outdoor', 'klasická (letná)'),
    ('indoor', 'halová (zimná)'),
)

FORMATS = (
    ('man', 'Man'),
    ('open', 'Open'),
    ('loose_mix', 'Loose Mix'),
    ('mix', 'Mix'),
    ('woman', 'Woman'),
)

REGIONS = (
    ('W', 'západ'),
    ('M', 'stred'),
    ('E', 'východ'),
    ('F', 'finále'),
)

STATUSES = (
    ('registered', 'zaregistrovaný'),
    ('invited', 'pozvaný'),
    ('waitlisted', 'čakajúci na pozvanie'),
    ('canceled', 'odmietnutý'),
    ('attended', 'zúčastnený'),
    ('not_attended', 'nezúčastnený'),
)

STATES = (
    ('not_public', 'nezverejnený'),
    ('public', 'čakajúci na otvorenie registrácie'),
    ('registration', 'registrácia tímov'),
    ('active', 'turnaj prebieha'),
    ('results', 'výsledky verejné'),
)


class Season(models.Model):
    orgs = models.ManyToManyField(
        User,
        limit_choices_to={
            'is_staff': True,
            'specialpermission__email_verified': True
        },
        blank=True,
        verbose_name='organizátori'
    )

    school_year = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex='^\d{4}\/\d{4}$',
                message='Školský rok musí byť vo formáte YYYY/YYYY.',
            ),
        ],
        verbose_name='školský rok'
    )

    season = models.CharField(
        max_length=31,
        choices=SEASONS,
        verbose_name='sezóna'
    )

    game_format = models.CharField(
        max_length=15,
        choices=FORMATS,
        default='loose_mix',
        verbose_name='hrací formát'
    )

    class Meta:
        verbose_name = 'sezóna'
        verbose_name_plural = 'sezóny'

    def __str__(self):
        return "{}, {}".format(self.season, self.school_year)


class TournamentManager(models.Manager):

    def get_queryset(self):
        return super(
            TournamentManager,
            self
        ).get_queryset().exclude(state='not_public')

    def get_previous(self):
        return self.exclude(
            date__gte=datetime.date.today(),
        ).order_by('-date')

    def get_next(self):
        return self.filter(
            date__gte=datetime.date.today(),
        ).order_by('-date')


class Tournament(models.Model):
    objects = models.Manager()
    public = TournamentManager()

    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        verbose_name='sezóna'
    )
    state = models.CharField(
        max_length=63,
        choices=STATES,
        default='registration',
        verbose_name='stav',
        help_text='Odvíjajú sa od neho akcie, ktoré môžu \
        návštevníci pri turnaji vykonávať.'
    )

    orgs = models.ManyToManyField(
        User,
        limit_choices_to={
            'is_staff': True,
            'specialpermission__email_verified': True
        },
        blank=True,
        verbose_name='organizátori'
    )

    delegate = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='delegát SAF'
    )
    director = models.CharField(
        max_length=255,
        default='Stredoškolská liga Ultimate Frisbee',
        verbose_name='riaditeľ turnaja',
        help_text='Ak si sponzor želá aby tu bol niekto iný, môže byť zmenené.'
    )
    institute = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='zastrešujúci inštitút',
        help_text='Môže ostať prázdne, podstatné je to iba ak si to vyžaduje sponzor.'
    )

    date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='dátum'
    )

    place = models.CharField(
        max_length=255,
        verbose_name='miesto konania',
        help_text='Miesto spolu s adresov, takže v tvare \
        napríklad "ihrisko, SOŠ Ostrovského 1, Košice".'
    )
    in_city = models.CharField(
        max_length=63,
        verbose_name='v meste',
        help_text='Mesto konania vyskloňované v lokále, napríklad "Košiciach".'
    )

    image = models.ImageField(
        upload_to='tournaments',
        verbose_name='obrázok',
        help_text='Bude zobrazený pri turnaji a jeho náhľade.')
    prop_image = models.ImageField(
        upload_to='tournaments/propositions',
        null=True,
        blank=True,
        verbose_name='logo do propozícií',
        help_text='V hlavičke propozícií bude na pravej strane \
        logo SAF a na ľavej toto logo, alebo ak nie je nahrané, logo SLU.'
    )

    cap = models.BooleanField(
        default=False,
        help_text='Budú zápasy s capom?'
    )
    game_duration = models.DurationField(
        blank=True,
        null=True,
        verbose_name='trvanie zápasu'
    )
    region = models.CharField(
        max_length=63,
        choices=REGIONS,
        verbose_name='región'
    )

    player_stats = models.BooleanField(
        default=False,
        verbose_name='hráčske štatistiky',
        help_text='Toto po začatí turnaja za žiadnych okolností nemeň! \
        Zaškrtni ak bude na turnaji súťaž aj o najlepšieho hráča, povolí \
        to pridávanie hráčov, ktorí skórovali a asistovali pri skórovaní.'
    )

    number_qualified = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2),
            MaxValueValidator(3),
        ],
        verbose_name='kvalifikovaní',
        help_text='Počet kvalifikovaných tímov.'
    )

    max_teams = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(6),
            MaxValueValidator(16),
        ],
        verbose_name='max. tímov',
        help_text='Maximálny počet tímov, ktoré budú na turnaj zavolané.'
    )
    signup_deadline = models.DateField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='dátum registrácie'
    )

    arrival_time = models.TimeField(
        default=datetime.time(8, 0),
        verbose_name='čas príchodu'
    )
    meeting_time = models.TimeField(
        default=datetime.time(8, 30),
        verbose_name='začiatok porady'
    )
    game_time = models.TimeField(
        default=datetime.time(8, 45),
        verbose_name='začiatok zápasov'
    )
    end_time = models.TimeField(
        default=datetime.time(14, 00),
        verbose_name='predpokladaný koniec'
    )

    class Meta:
        verbose_name = 'turnaj'
        verbose_name_plural = 'turnaje'

    def get_name(self):
        if self.region == 'F':
            temp = 'finále'
        elif self.region == 'W':
            temp = 'západoslovenské regionálne kolo'
        elif self.region == 'M':
            temp = 'stredoslovenské regionálne kolo'
        elif self.region == 'E':
            temp = 'východoslovenské regionálne kolo'
        else:
            raise ValueError('Value must match region, \
            could not be {}!'.format(self.region))

        if self.season.season == 'indoor':
            name = 'Halové ' + temp
        else:
            name = '' + temp[0].upper() + temp[1:]

        name += ' SLU ' + self.season.school_year
        return name

    def team_count(self):
        return len(Team.objects.filter(
            tournament=self.id
        ))

    def confirmed_team_count(self):
        return len(Team.objects.filter(
            tournament=self.id,
            confirmed=True
        ))

    def is_registration_open(self):
        if (
            self.signup_deadline >= datetime.date.today() and
            self.state != 'public' and
            self.region != 'F'
        ):
            return True
        else:
            return False

    def is_next(self):
        if self.date >= datetime.date.today():
            return True
        else:
            return False

    def __str__(self):
        return "{}".format(self.get_name())


class Team(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        verbose_name='turnaj'
    )

    confirmed = models.BooleanField(
        default=False,
        verbose_name='registrácia potvrdená'
    )
    status = models.CharField(
        max_length=63,
        choices=STATUSES,
        default='registered'
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        verbose_name='škola'
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        verbose_name='učiteľ'
    )
    players = models.ManyToManyField(
        Player,
        related_name='team',
        verbose_name='súpiska',
        blank=True
    )

    name = models.CharField(
        max_length=31,
        null=True,
        blank=True,
        verbose_name='názov tímu'
    )
    extra_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='kontaktný email',
        help_text='Všetka komunikácia s tímom bude prebiehať \
        s učiteľom prostredníctvo jeho e-mailovej adresy. \
        AK chcete aby aj niekto iný dostával správy o turnaji, \
        zadajtu tu jeho email.'
    )

    identifier = models.UUIDField(
        primary_key=False,
        default=uuid4,
        editable=False,
        verbose_name='identifikátor'
    )
    accept_gdpr = models.BooleanField(
        default=True,
        verbose_name='akceptovali GDPR',
        help_text='Keďže SAF neprejavila záujem starať sa o GDPR \
        a iné právne veci, toto pole je prednastavené ako zaškrtnuté \
        a tímy ho zatiaľ nedokážu ovplyvniť.'
    )

    class Meta:
        verbose_name = 'tím'
        verbose_name_plural = 'tímy'

    def get_name(self):
        if self.name:
            return self.name
        else:
            return self.school

    def get_emails(self):
        email_list = [self.teacher.email]
        if self.extra_email:
            email_list.append(self.extra_email)

        return email_list

    def __str__(self):
        return "{}".format(self.get_name())


class Result(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.PROTECT,
        verbose_name='turnaj'
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        verbose_name='tím'
    )
    place = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(16),
        ],
        verbose_name='umiestnenie'
    )

    class Meta:
        verbose_name = 'výsledok'
        verbose_name_plural = 'výsledky'

    def __str__(self):
        return "{}. {} - {}".format(
            self.place,
            self.team.get_name(),
            self.tournament.get_name(),
        )


class Match(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        verbose_name='turnaj'
    )
    begining_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='začiatok'
    )

    home_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='home_team',
        verbose_name='domáci tím'
    )
    host_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='host_team',
        verbose_name='hosťujúci tím'
    )

    class Meta:
        verbose_name = 'zápas'
        verbose_name_plural = 'zápasy'

    def __str__(self):
        return "{} vs. {}".format(
            self.home_team,
            self.host_team
        )


class Point(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        verbose_name='zápas'
    )
    time = models.TimeField(
        default=datetime.datetime.now().time(),
        verbose_name='čas'
    )

    score = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='score',
        blank=True,
        null=True,
        verbose_name='skórujúci'
    )
    assist = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='assist',
        blank=True,
        null=True,
        verbose_name='asistujúci'
    )

    class Meta:
        verbose_name = 'bod'
        verbose_name_plural = 'body'

    def __str__(self):
        return "{} - {}".format(
            str(self.time),
            self.match
        )


@deconstructible
class PathAndRename(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = 'image_{}.{}'.format(instance.pk, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)


class Photo(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        verbose_name='turnaj'
    )

    image = models.ImageField(
        upload_to=PathAndRename(
            os.path.join(
                settings.MEDIA_ROOT,
                'tournaments'
            )
        ),
        verbose_name='fotka'
    )

    class Meta:
        verbose_name = 'fotka'
        verbose_name_plural = 'fotky'

    def __str__(self):
        return "Image {} - {}".format(self.pk, self.tournament.get_name())
