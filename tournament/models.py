from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.db import models
from django.utils import timezone
from django.core.validators import (
    RegexValidator,
    MaxValueValidator,
    MinValueValidator
)
from django.contrib import messages
from django.shortcuts import redirect

import os
from uuid import uuid4
import datetime

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from PIL import Image
from zipfile import ZipFile
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import PermissionDenied

from emails.emails import SendMail
from user.models import User
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
        limit_choices_to={'is_staff': True},
        blank=True,
        verbose_name='organizátori',
        help_text='Centrálni organizátori sezóny.'
    )

    school_year = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex='^\d{4}\/\d{4}$',
                message='Školský rok musí byť vo formáte YYYY/YYYY.',
            ),
        ],
        verbose_name='školský rok',
        help_text='Školský rok vo formáte YYYY/YYYY.'
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
        default='public',
        verbose_name='stav',
        help_text='Odvíjajú sa od neho akcie, ktoré môžu \
        návštevníci pri turnaji vykonávať. Mení sa prostredníctvom \
        funkcií pri zozname turnajov.'
    )

    orgs = models.ManyToManyField(
        User,
        limit_choices_to={'is_staff': True},
        blank=True,
        verbose_name='organizátori',
        help_text='Lokálni organizátori turnaja.'
    )
    scorekeepers = models.ManyToManyField(
        User,
        limit_choices_to={'is_staff': True},
        blank=True,
        verbose_name='zapisovatelia skóre',
        help_text='Používatelia s povoleným zapisovaním skóre.',
        related_name='tournament_scoring',
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

    def change_state(self, new):
        if new == 'not_public': # zosukromnit
            self.state = new
        elif new == 'public': # zverejnit
            self.state = new
        elif new == 'registration': # otvorit registraciu
            self.state = new
            self.registration_open_notification()
        elif new == 'active': # zacat turnaj
            self.state = new
            recipients = []
            for org in self.orgs.all():
                recipients.append(org.email)
            for org in self.season.orgs.all():
                recipients.append(org.email)
            SendMail(
                recipients,
                'Turnaj '+str(self)+' začal'
            ).tournament_activation(self)
        elif new == 'results': # zverejnit vysledky
            if self.state in ['active', 'public'] and \
                len(Result.objects.filter(tournament=self)) > 0:
                self.state = new
                self.send_certificate()
            else:
                return 'Výsledky buď neexistujú, alebo stav turnaja '+\
                    'nepovoľuje ich zverejnenie.'
        else:
            return 'Stav neexistuje.'

        self.save()
        return None

    def send_certificate(self):
        teams = Team.objects.filter(
            tournament=self,
            status='attended',
        )

        max_spirit = 0
        sotg_winner = None
        for team in teams:
            result = Result.objects.get(
                tournament=self,
                team=team,
            ).place

            SendMail(
                team.get_emails(),
                str(self) + ' - výsledky',
            ).result_email(team, result)

            scores = SpiritScore.objects.filter(
                tournament=self,
                to_team=team,
            )
            s = SpiritScore.sum_score(scores)
            if s > max_spirit:
                max_spirit = s
                sotg_winner = team
        
        if sotg_winner is not None:
            SendMail(
                sotg_winner.get_emails(),
                str(self) + ' - výsledky',
            ).result_email(team, result, sotg=True)

    def registration_open_notification(self):
        if self.region != 'F':
            tournaments = Tournament.objects.filter(
                region=self.region,
            )
            teams = Team.objects.filter(
                tournament__in=tournaments,
            )

            recipients = []
            for team in teams:
                recipients += team.get_emails()

            SendMail(
                recipients,
                '{}'.format(str(self)),
                bcc=True
            ).registration_open_notification(self.pk)


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

    def __str__(self):
        return "{}".format(self.get_name())

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

    def attend(self):
        if self.status == 'invited':
            self.status = 'attended'
            self.save()
            return 'Stav tímu {} bol zmenený na zúčastnený.'.format(self.name), messages.SUCCESS
        else:
            return 'Tím {} nebol pozvaný na turnaj {}, preto sa ho nemôže zúčastniť.'.format(
                self.name,
                self.tournament
            ), messages.WARNING

    def invite(self):
        if self.status == 'waitlisted':
            self.status = 'invited'
            self.save()

            SendMail(
                self.get_emails(),
                'Pozvánka na {}'.format(self.tournament)
            ).team_invitation(self)

            return 'Tím {} bol pozvaný na {}.'.format(self.name, self.tournament), messages.SUCCESS
        elif self.status == 'invited':
            return 'Tím {} už bol pozvaný.'.format(self.name), messages.WARNING
        else:
            return 'Tím {} nemá potvrdenú registráciu a preto nemôže byť pozvaný.'.format(self.name), messages.WARNING

    def cancel(self):
        self.status = 'canceled'
        self.save()

        return 'Tím {} bol odmietnutý.'.format(self.name)

    def not_attend(self):
        if self.status == 'invited':
            self.status = 'not_attended'
            self.save()

            return 'Stav tím {} bol zmenený na nezúčastnený.'.format(self.name)
        else:
            return 'Tím {} nemôže byť označený za nezúčastnený, pretože sa turnaja zúčastniť nemal.'.format(self.name)

    def checkin(self, tournament):
        if self.tournament == tournament:
            if self.status == 'invited':
                self.status = 'attended'
                self.save()

                Checkin.objects.create(
                    team=self,
                    time_created=timezone.now(),
                ).save()

                SendMail(
                    self.get_emails(),
                    '{} - potvrdenie účasti'.format(str(tournament)),
                ).attendee_email(self)

                return None
            else:
                return 'Tento tím na turnaj nebol pozvaný'
        else:
            return 'Turnaj sa nezhoduje s tímom'


class Checkin(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name='tím'
    )
    time_created = models.DateTimeField(
        verbose_name='čas vytvorenia',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'kontrola'
        verbose_name_plural = 'kontroly'

    def __str__(self):
        return '{} - {}'.format(
            str(self.time_created),
            self.team.get_name()
        )


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
        verbose_name='čas',
        help_text='Čas v ktorom bod padol.'
    )

    score = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='score',
        blank=True,
        null=True,
        verbose_name='skórujúci',
        help_text='Hráč, ktorý dal bod.'
    )
    assist = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='assist',
        blank=True,
        null=True,
        verbose_name='asistujúci',
        help_text='Hráč, ktorý prihral na bod.'
    )

    class Meta:
        verbose_name = 'bod'
        verbose_name_plural = 'body'

    def __str__(self):
        return "{} - {}".format(
            str(self.time),
            self.match
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.time = timezone.now()

        super(Point, self).save(*args, **kwargs)


class SpiritScore(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        verbose_name='turnaj',
    )
    from_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='spirit_from',
        verbose_name='od tímu',
    )
    to_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='spirit_to',
        verbose_name='pre tím',
    )

    rules = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4),
        ],
        verbose_name='znalosť a použitie pravidiel',
        default=2,
    )
    fouls = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4),
        ],
        verbose_name='fouly a telesný kontakt',
        default=2,
    )
    fair = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4),
        ],
        verbose_name='férové zmýšľanie',
        default=2,
    )
    selfcontrol = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4),
        ],
        verbose_name='pozitívny prístup a sebaovládanie',
        default=2,
    )
    communication = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4),
        ],
        verbose_name='komunikácia',
        default=2,
    )
    note = models.TextField(
        blank=True,
        verbose_name='poznámka'
    )

    class Meta:
        verbose_name = 'SOTG'
        verbose_name_plural = 'SOTG'

    def __str__(self):
        return "{} bodov od {} pre {}".format(
            str(self.rules+self.fouls+self.fair+self.selfcontrol+self.communication),
            self.from_team,
            self.to_team,
        )

    @classmethod
    def sum_score(self, spirits):
        s = 0
        for spirit in spirits:
            s += sum([
                spirit.rules,
                spirit.fouls,
                spirit.fair,
                spirit.selfcontrol,
                spirit.communication
            ])
        return s

    @classmethod
    def sum_rules(self, spirits):
        s = 0
        for spirit in spirits:
            s += spirit.rules
        return s

    @classmethod
    def sum_fouls(self, spirits):
        s = 0
        for spirit in spirits:
            s += spirit.fouls
        return s

    @classmethod
    def sum_fair(self, spirits):
        s = 0
        for spirit in spirits:
            s += spirit.fair
        return s

    @classmethod
    def sum_selfcontrol(self, spirits):
        s = 0
        for spirit in spirits:
            s += spirit.selfcontrol
        return s

    @classmethod
    def sum_communication(self, spirits):
        s = 0
        for spirit in spirits:
            s += spirit.communication
        return s


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

    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 225)],
        format='JPEG',
        options={'quality': 60}
    )

    class Meta:
        verbose_name = 'fotka'
        verbose_name_plural = 'fotky'

    def __str__(self):
        return "Fotka {} - {}".format(self.pk, self.tournament.get_name())


class AbstractGallery(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        verbose_name='turnaj'
    )
    zip_file = models.FileField(
        blank=True,
        upload_to='galleries',
        verbose_name='súbor ZIP'
    )

    class Meta:
        verbose_name = 'fotky zo súboru ZIP'
        verbose_name_plural = 'fotky zo súborov ZIP'

    def __str__(self):
        return "Galéria {} - {}".format(self.pk, self.tournament.get_name())

    def save(self, delete_zip_file=True, *args, **kwargs):
        super(AbstractGallery, self).save(*args, **kwargs)
        if self.zip_file:
            zf = ZipFile(self.zip_file)
            for name in zf.namelist():
                data = zf.read(name)
                try:
                    image = Image.open(BytesIO(data))
                    image.load()
                    image = Image.open(BytesIO(data))
                    image.verify()
                except ImportError:
                    print('import error')
                '''
                except:
                    print('iny error')
                    continue
                '''
                name = os.path.split(name)[1]
                path = os.path.join(
                    settings.MEDIA_ROOT,
                    'tournaments',
                    str(name)
                )
                saved_path = default_storage.save(path, ContentFile(data))
                p = Photo.objects.create(
                    tournament=self.tournament,
                    image=saved_path
                )
                p.save()
            if delete_zip_file:
                zf.close()
                self.zip_file.delete(save=True)
