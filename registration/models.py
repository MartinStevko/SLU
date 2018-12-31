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
    name = models.CharField(max_length=255)
    web = models.URLField(max_length=255)

    street = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex='^[ a-zA-ZáäčďéěíĺľňóŕřšťúýžÁČĎÉĚÍĹĽŇÓŔŘŠŤÚÝŽ]{3,}[\/0-9]{1,10}$',
                message='Ulica musí byť vo formáte Hlavná pri Rieke 14.',
            )
        ]
    )
    postcode = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex='^\d{3} \d{2}$',
                message='PSČ musí byť vo formáte 123 45.',
            )
        ]
    )
    city = models.CharField(max_length=255)
    region = models.CharField(
        max_length=255,
        choices=REGIONS
    )

    have_disc = models.BooleanField(default=False)

    def __str__(self):
        return "{}, {}, {} {}".format(
            self.name,
            self.street,
            self.postcode,
            self.city
        )


class Teacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    email = models.EmailField()

    phone_number = models.CharField(
        max_length=31,
        validators=[
            RegexValidator(
                regex='^\+42(1|0)( \d{3}){3}$',
                message='Telefónne číslo musí byť vo formáte +421 123 456 789.',
            ),
        ]
    )

    def __str__(self):
        return "{} {}".format(
            self.first_name,
            self.last_name
        )


class Player(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    sex = models.CharField(
        max_length=7,
        choices=GENDERS
    )

    is_exception = models.BooleanField(default=False)

    def __str__(self):
        return "{} {}".format(
            self.first_name,
            self.last_name
        )
