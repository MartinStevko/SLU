from django.forms import ModelForm, Form, BooleanField
from .models import Teacher, Team, Player

class GDPR(Form):
    suhlas_ou = BooleanField(label='Súhlasím so spracovaním osobných údajov v rozsahu vyššie uvedenom', required=False)
    suhlas_mf = BooleanField(label='Súhlasím so zverejnením fotiek a videí, na ktorých som, zhotovených počas SLU za účelom propagácie súťaže', required=False)

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['pohlavie', 'meno', 'bageta']

        labels = {
            'pohlavie' : 'Pohlavie',
            'meno' : 'Meno a priezvisko hráča',
            'bageta' : '',
        }

    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.fields['bageta'].widget.attrs.update({'class': 'last-one'})

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ['meno', 'mail', 'tel_cislo']

        labels = {
            'meno' : 'Meno a priezvisko učiteľa',
            'mail' : 'E-mail učiteľa',
            'tel_cislo' : 'Telefónne číslo učiteľa',
        }

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = [
            'region',

            'meno',
            'diplom_meno',

            'mail',
            'tel_cislo',

            'skola',
            'adresa',
            'okres',
            'kraj',

            'pesnicka',
            'sprava',
        ]

        labels = {
            'meno' : 'Meno tímu',
            'diplom_meno' : 'Meno tímu na diplome',

            'mail' : 'Kontaktný e-mail',
            'tel_cislo' : 'Kontaktné telefónne číslo',

            'skola' : 'Názov školy',
            'adresa' : 'Adresa školy',
            'okres' : 'Okres',
            'kraj' : 'Kraj',
            'region' : 'Región',

            'pesnicka' : 'Tímová pesnička (link)',
            'sprava' : 'Správa organizátorom',
        }
