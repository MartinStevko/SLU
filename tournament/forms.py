from django import forms
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from tournament.models import Point, SpiritScore

from django.utils import timezone


class ScoringForm(OverwriteOnlyModelFormMixin, BetterModelForm):

    def fieldsets(self):
        self._fieldsets = [(None, {'fields': ('score', 'assist')}),]

        return super(ScoringForm, self).fieldsets

    class Meta:
        model = Point

        labels = {
            'score': 'Skórujúci hráč',
            'assist': 'Asistujúci hráč',
        }

        exclude = ['time', 'match']


class SpiritForm(OverwriteOnlyModelFormMixin, BetterModelForm):

    def fieldsets(self):
        self._fieldsets = [(None, {'fields': ('from_team', 'to_team', 
        'rules', 'fouls', 'fair', 'selfcontrol', 'communication', 'note')}),]

        return super(SpiritForm, self).fieldsets

    class Meta:
        model = SpiritScore

        labels = {
            'from_team': 'Môj tím',
            'to_team': 'Súper',
        }

        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

        exclude = ['tournament']
