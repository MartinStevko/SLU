from django.db import models

bagety = (
    ('M', 'mäsová bageta'),
    ('V', 'vegetariánska bageta'),
    ('N', 'nechce bagetu'),
)

pohlavia = (
    ('M', 'muž'),
    ('W', 'žena'),
)

regiony = (
    ('Z', 'západné Slovensko'),
    ('S', 'stredné Slovensko'),
    ('V', 'východné Slovensko'),
)

kraje = (
    ('BA', 'Bratislavský kraj'),
    ('TT', 'Trnavský kraj'),
    ('NI', 'Nitriansky kraj'),
    ('TN', 'Trenčiansky kraj'),
    ('BB', 'Banskobystrický kraj'),
    ('ZI', 'Žilinský kraj'),
    ('KE', 'Košický kraj'),
    ('PO', 'Prešvský kraj'),
)


class Teacher(models.Model):
    meno = models.CharField(max_length=100)
    mail = models.EmailField()
    tel_cislo = models.CharField(max_length=13)

    def __str__(self):
        return "{}".format(self.meno)

    class Meta:
        verbose_name = 'učiteľ'
        verbose_name_plural = 'učitelia'


class Team(models.Model):
    meno = models.CharField(max_length=30, unique=True)
    diplom_meno = models.CharField(max_length=15, unique=True)
    kvalifikovany = models.BooleanField(default=False)

    region = models.CharField(max_length=100, choices=regiony)
    kraj = models.CharField(max_length=100, choices=kraje)
    okres = models.CharField(max_length=100)
    skola = models.CharField(max_length=100)
    adresa = models.CharField(max_length=200)

    ucitel = models.ForeignKey(Teacher, on_delete=models.PROTECT)

    mail = models.EmailField()
    tel_cislo = models.CharField(max_length=13)

    pesnicka = models.URLField(max_length=200)
    sprava = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.meno)

    class Meta:
        verbose_name = 'tím'
        verbose_name_plural = 'tímy'


class Player(models.Model):
    tim = models.ForeignKey(Team, on_delete=models.CASCADE)
    meno = models.CharField(max_length=100)
    bageta = models.CharField(max_length=100, choices=bagety)
    pohlavie = models.CharField(max_length=100, choices=pohlavia)

    def __str__(self):
        return "{} - {}".format(self.meno, self.tim.meno)

    class Meta:
        verbose_name = 'hráč'
        verbose_name_plural = 'hráči'


class FinalMember(models.Model):
    tim = models.ForeignKey(Team, on_delete=models.CASCADE)
    meno = models.CharField(max_length=100)
    bageta = models.CharField(max_length=20, choices=bagety, blank=True)
    pohlavie = models.CharField(max_length=100, choices=pohlavia)

    def __str__(self):
        return "{} - {}".format(self.meno, self.tim.meno)

    class Meta:
        verbose_name = 'hráč (finále)'
        verbose_name_plural = 'hráči (finále)'
