from django.db import models
from django.core.validators import RegexValidator

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
        verbose_name='Názov'
    )
    web = models.URLField(
        max_length=255,
        verbose_name='Webová stránka'
    )

    street = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex='^[ a-zA-ZáäčďéěíĺľňóŕřšťúýžÁČĎÉĚÍĹĽŇÓŔŘŠŤÚÝŽ]{3,}[\/0-9]{1,10}$',
                message='Ulica musí byť vo formáte Hlavná pri Rieke 14.',
            )
        ],
        verbose_name='Ulica'
    )
    postcode = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex='^\d{3} \d{2}$',
                message='PSČ musí byť vo formáte 123 45.',
            )
        ],
        verbose_name='PSČ'
    )
    city = models.CharField(
        max_length=255,
        verbose_name='Mesto (obec)'
    )
    region = models.CharField(
        max_length=255,
        choices=REGIONS,
        verbose_name='Kraj'
    )

    have_disc = models.BooleanField(
        default=False,
        verbose_name='Dostali disk'
    )

    class Meta:
        verbose_name = 'škola'
        verbose_name_plural = 'školy'

    def __str__(self):
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
        verbose_name='Škola'
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='Meno'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Priezvisko'
    )

    email = models.EmailField(verbose_name='E-mail')

    phone_number = models.CharField(
        max_length=31,
        validators=[
            RegexValidator(
                regex='^\+42(1|0)( \d{3}){3}$',
                message='Telefónne číslo musí byť vo formáte +421 123 456 789.',
            ),
        ],
        verbose_name='Telefónne číslo'
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
        verbose_name='Škola'
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='Meno'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Priezvisko'
    )
    sex = models.CharField(
        max_length=7,
        choices=GENDERS,
        verbose_name='Pohlavie'
    )

    is_exception = models.BooleanField(
        default=False,
        verbose_name='Je výnimka'
    )

    class Meta:
        verbose_name = 'hráč'
        verbose_name_plural = 'hráči'

    def __str__(self):
        return "{} {}".format(
            self.first_name,
            self.last_name
        )
