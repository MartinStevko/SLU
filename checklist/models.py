from django.db import models
from django.contrib import messages

from tournament.models import Tournament

PHASES = (
    ('1_pre_reg', 'pred registráciou'),
    ('2_pre_tour', 'pred turnajom'),
    ('3_on_place', 'na mieste'),
    ('4_post_tour', 'po turnaji'),
)


class Task(models.Model):
    name = models.CharField(
        max_length=63,
        verbose_name='meno',
    )
    phase = models.CharField(
        max_length=31,
        choices=PHASES,
        verbose_name='fáza'
    )
    description = models.TextField(
        verbose_name='popis',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'úloha'
        verbose_name_plural = 'úlohy'

    def __str__(self):
        return "{}".format(self.name)


class Checklist(models.Model):
    tournament = models.OneToOneField(
        Tournament,
        on_delete=models.PROTECT,
        related_name='checklist',
        verbose_name='turnaj',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'zoznam úloh'
        verbose_name_plural = 'zoznamy úloh'

    def __str__(self):
        if self.tournament:
            return "Zoznam úloh - {}".format(str(self.tournament))
        else:
            return "Kópia zoznamu úloh ({})".format(self.pk)


class TaskStatus(models.Model):
    checklist = models.ForeignKey(
        Checklist,
        on_delete=models.CASCADE,
        verbose_name='zoznam',
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        verbose_name='úloha'
    )

    done = models.BooleanField(
        default=False,
        verbose_name='dokončená'
    )

    class Meta:
        verbose_name = 'stav úloh'
        verbose_name_plural = 'stavy úloh'
    
    def __str__(self):
        return "{}".format(str(self.task))

    def duplicate(self, checklist):
        t = TaskStatus.objects.create(
            checklist=checklist,
            task=self.task,
            done=False
        )
