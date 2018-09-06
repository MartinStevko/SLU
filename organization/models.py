from django.db import models

class Teacher(models.Model):
    meno = models.CharField(max_length=100)
    mail = models.EmailField()
    tel_cislo = models.CharField(max_length=13)

    def __str__(self):
        return "{}".format(self.meno)

class Player(models.Model):
    meno = models.CharField(max_length=100)
    bageta = models.CharField(max_length=20)

    def __str__(self):
        return "{}".format(self.meno)

class Team(models.Model):
    meno = models.CharField(max_length=30, unique=True)
    diplom_meno = models.CharField(max_length=15, unique=True)
    kvalifikovany = models.BooleanField(default=False)

    region = models.CharField(max_length=100)
    kraj = models.CharField(max_length=100)
    okres = models.CharField(max_length=100)
    skola = models.CharField(max_length=100)
    adresa = models.CharField(max_length=200)

    ucitel = models.ForeignKey(Teacher, on_delete=models.PROTECT)

    kapitan = models.CharField(max_length=100)
    mail = models.EmailField()
    tel_cislo = models.CharField(max_length=13)

    supiska = models.ManyToManyField(Player)

    pesnicka = models.URLField(max_length=200)
    sprava = models.TextField()

    def __str__(self):
        return "{}".format(self.meno)

class FinalMember(models.Model):
    tim = models.ForeignKey(Team, on_delete=models.CASCADE)
    clenovia = models.ManyToManyField(Player)

    def __str__(self):
        return "{} - súpiska".format(self.tim.meno)
