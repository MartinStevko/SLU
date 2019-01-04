from django import forms
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from tournament.models import Point


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
