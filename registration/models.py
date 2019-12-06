from django.db import models
from django.core.validators import (
    RegexValidator,
    MaxValueValidator,
    MinValueValidator
)

GENDERS = (
    ('male', 'muž'),
    ('female', 'žena'),
)

REGIONS = (
    ('BA', 'Bratislavský kraj'),
    ('TT', 'Trnavský kraj'),
    ('TN', 'Trenčiansky kraj'),
    ('NI', 'Nitriansky kraj'),
    ('ZI', 'Žilinský kraj'),
    ('BB', 'Banskobystrický kraj'),
    ('PO', 'Prešovský kraj'),
    ('KE', 'Košický kraj'),
)


class School(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='názov'
    )
    web = models.URLField(
        max_length=255,
        verbose_name='webová stránka',
        help_text='Webové sídlo školy.'
    )

    street = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex='^[ a-zA-ZáäčďéěíĺľňóŕřšťúýžÁČĎÉĚÍĹĽŇÓŔŘŠŤÚÝŽ]{3,}[\/0-9]{1,10}$',
                message='Ulica musí byť vo formáte Hlavná pri Rieke 14.',
            )
        ],
        verbose_name='ulica',
        help_text='Názov ulice bez čiarok, pomlčiek a iných \
        špeciálnych znakov spolu s popisným číslom.'
    )
    # Warnign! Forms.py rely exactly on this Regex pattern.
    postcode = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex='^\d{3} \d{2}$',
                message='PSČ musí byť vo formáte 123 45.',
            )
        ],
        verbose_name='PSČ',
        help_text='Poštové smerové číslo v tvare "123 45".'
    )
    city = models.CharField(
        max_length=255,
        verbose_name='mesto (obec)'
    )
    region = models.CharField(
        max_length=255,
        choices=REGIONS,
        verbose_name='kraj'
    )

    have_disc = models.BooleanField(
        default=False,
        verbose_name='dostali disk'
    )

    class Meta:
        verbose_name = 'škola'
        verbose_name_plural = 'školy'

    def __str__(self):
        # Warnign! Forms.py rely exactly on this pattern.
        return "{}, {}, {} {}".format(
            self.name,
            self.street,
            self.postcode,
            self.city
        )


class Teacher(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        verbose_name='škola'
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='meno'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='priezvisko'
    )

    email = models.EmailField(verbose_name='e-mail')

    phone_number = models.CharField(
        max_length=31,
        validators=[
            RegexValidator(
                regex='^\+42(1|0)( \d{3}){3}$',
                message='Telefónne číslo musí byť vo formáte +421 123 456 789.',
            ),
        ],
        verbose_name='telefónne číslo',
        help_text='Telefonné číslo oddelené medzerami po trojčísliach \
        na začiatku s predvoľbou.'
    )

    class Meta:
        verbose_name = 'učiteľ'
        verbose_name_plural = 'učitelia'

    def __str__(self):
        return "{} {}".format(
            self.first_name,
            self.last_name
        )


class Player(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        verbose_name='škola'
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='meno'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='priezvisko'
    )
    sex = models.CharField(
        max_length=7,
        choices=GENDERS,
        verbose_name='pohlavie'
    )
    number = models.SmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(99),
        ],
        verbose_name='číslo',
    )

    is_exception = models.BooleanField(
        default=False,
        verbose_name='je výnimka'
    )

    class Meta:
        verbose_name = 'hráč'
        verbose_name_plural = 'hráči'

    def __str__(self):
        if self.number or self.number == 0:
            return "{} {} ({})".format(
                self.first_name,
                self.last_name,
                self.number,
            )
        else:
            return "{} {}".format(
                self.first_name,
                self.last_name
            )
