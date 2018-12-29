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
from datetime import time, timedelta

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

ROLES = (
    ('P', 'bod'),
    ('A', 'asistencia'),
)


class Season(models.Model):
    orgs = models.ManyToManyField(
        User,
        limit_choices_to={
            'is_staff': True,
            'specialpermission__email_verified': True
        }
    )

    school_year = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex='^\d{4}\/\d{4}$',
                message='Školský rok musí byť vo formáte YYYY/YYYY.',
            ),
        ]
    )

    season = models.CharField(
        max_length=31,
        choices=SEASONS
    )

    game_format = models.CharField(
        max_length=15,
        choices=FORMATS,
        default='loose_mix'
    )

    def __str__(self):
        return "{}, {}".format(self.season, self.school_year)


class Tournament(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT
    )

    orgs = models.ManyToManyField(
        User,
        limit_choices_to={
            'is_staff': True,
            'specialpermission__email_verified': True
        }
    )

    delegate = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    institute = models.CharField(max_length=255)

    date = models.DateField(
        auto_now=False,
        auto_now_add=False
    )

    place = models.CharField(max_length=255)
    in_city = models.CharField(max_length=63)

    image = models.ImageField(upload_to='tournaments')
    prop_image = models.ImageField(upload_to='tournaments/propositions')

    cap = models.BooleanField(default=False)
    game_duration = models.DurationField(default=timedelta(0, 720))
    region = models.CharField(
        max_length=63,
        choices=REGIONS
    )

    player_stats = models.BooleanField(default=False)

    number_qualified = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2),
            MaxValueValidator(3),
        ]
    )

    max_teams = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(6),
            MaxValueValidator(16),
        ]
    )
    signup_deadline = models.DateTimeField(
        auto_now=False,
        auto_now_add=False
    )

    arrival_time = models.TimeField(default=time(8, 0))
    meeting_time = models.TimeField(default=time(8, 30))
    game_time = models.TimeField(default=time(8, 45))
    end_time = models.TimeField(default=time(14, 00))

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

    def __str__(self):
        return "{}".format(self.get_name())


class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT)
    players = models.ManyToManyField(Player)

    name = models.CharField(
        max_length=31,
        null=True,
        blank=True
    )

    identifier = models.UUIDField(
        primary_key=False,
        default=uuid4,
        editable=False
    )
    accept_gdpr = models.BooleanField(default=False)

    def get_name(self):
        if self.name:
            return self.name
        else:
            return self.school

    def __str__(self):
        return "{}".format(self.school)


class Result(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)

    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    place = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(16),
        ]
    )

    def __str__(self):
        return "{}. {} - {}".format(
            self.place,
            self.team.get_name(),
            self.tournament.get_name(),
        )


class Match(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE
    )
    begining_time = models.DateTimeField(
        blank=True,
        null=True
    )

    home_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='home_team'
    )
    host_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='host_team'
    )

    class Meta:
        verbose_name_plural = 'matches'

    def __str__(self):
        return "{} vs. {}".format(
            self.home_team,
            self.host_team
        )


class Point(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE
    )
    time = models.DurationField()

    score = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='score',
        blank=True,
        null=True
    )
    assist = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name='assist',
        blank=True,
        null=True
    )

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
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    image = models.ImageField(upload_to=PathAndRename(
        os.path.join(
            settings.MEDIA_ROOT,
            'tournaments'
        )
    ))

    def __str__(self):
        return "Image {} - {}".format(self.pk, self.tournament.get_name())
