from django.forms import ModelForm, Form, CharField, ChoiceField, BooleanField
from .models import Teacher, Team

bagety = (
    ('M', 'mäsová bageta'),
    ('V', 'vegetariánska bageta'),
)

class GDPR(Form):
    suhlas_ou = BooleanField(label='Súhlasím so spracovaním osobných údajov v rozsahu vyššie uvedenom', required=False)
    suhlas_mf = BooleanField(label='Súhlasím so zverejnením fotiek a videí zhotovených počas SLU za účelom propagácie súťaže', required=False)

class PlayerForm(Form):
    meno = CharField(label='Meno a priezvisko hráča', max_length=100)
    bageta = ChoiceField(label='', choices=bagety)

class UnPlayerForm(Form):
    meno = CharField(label='Meno a priezvisko hráča', max_length=100, required=False)
    bageta = ChoiceField(label='', choices=bagety)

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
