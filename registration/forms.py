from django import forms
from django.forms import modelformset_factory
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from registration.models import *
from tournament.models import Team


class SchoolForm(OverwriteOnlyModelFormMixin, BetterModelForm):

    choose_school = forms.CharField(
        label='Registrovaná škola',
        help_text='Ak nevidíte vašu školu v zozname, vytvorte novú, nabudúce ju tu už uvidíte.',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'typeahead'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()

        values = []
        for field in self.fields:
            if field != 'choose_school':
                values.append(cleaned_data.get(field))

        choose_school = cleaned_data.get('choose_school')

        if not choose_school:
            for field in values:
                if not field:
                    raise forms.ValidationError('Školu musíš buď \
                    vybrať z existujúcich, alebo vytvoriť novú.')
        
        else:
            try:
                name, street, city = choose_school.split(', ')
                cleaned_data['choose_school'] = School.objects.get(
                    name=name,
                    street=street,
                    city=city[7:]
                ).pk
            except(School.DoesNotExist, ValueError):
                raise forms.ValidationError('Takáto škola v zozname nie je. Vyber \
                buď presný názov školy zo zoznamu, alebo školu vytvor.')

    def fieldsets(self):
        self._fieldsets = [
            (
                'Vybrať školu',
                {'fields': ('choose_school',),
                 'description': 'Vyberte školu zo zoznamu nižšie, alebo \
                 vytvorte novú školu. Všetci hráči musia byť žiakmi tejto \
                 školy a pod jej menom zároveň budú súťažiť.',
                }
            ),
            (
                'Vytvoriť školu',
                {'fields': ('name', 'web', 'street', 'postcode', 'city', 'region'),
                 'description': 'Vyberte školu zo zoznamu vyššie, alebo \
                 vytvorte novú školu. Všetci hráči musia byť žiakmi tejto \
                 školy a pod jej menom zároveň budú súťažiť.',
                }
            ),
        ]

        return super(SchoolForm, self).fieldsets

    class Meta:
        model = School

        exclude = ['have_disc']


class TeacherForm(OverwriteOnlyModelFormMixin, BetterModelForm):

    def fieldsets(self):
        self._fieldsets = [
            (
                'Učiteľ',
                {'fields': ('first_name', 'last_name', 'email', 'phone_number'),
                 'description': 'Údaje učiteľa z vašej školy, \
                 ktorý vás na turnaji bude sprevádzať.',
                }
            ),
        ]

        return super(TeacherForm, self).fieldsets

    class Meta:
        model = Teacher

        exclude = ['school']


class TeamForm(OverwriteOnlyModelFormMixin, BetterModelForm):
    message = forms.CharField(
        widget=forms.Textarea,
        label='Správa',
        help_text='Máte nejaké otázky, požiadavky, alebo nám \
        len chcete poslať odkaz? Tu je na to miesto.',
        required=False
    )

    def fieldsets(self):
        self._fieldsets = [
            (
                'Tím',
                {'fields': ('extra_email', 'message',)}
            ),
        ]

        return super(TeamForm, self).fieldsets

    class Meta:
        model = Team

        fields = ('extra_email', 'message')


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player

        fields = ['first_name', 'last_name', 'sex', 'number']

PlayerFormSet = modelformset_factory(
    Player,
    form=PlayerForm,
    max_num=10,
    extra=10
)
