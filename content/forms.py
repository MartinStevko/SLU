from django import forms
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from content.models import Message


class ContactForm(OverwriteOnlyModelFormMixin, BetterModelForm):

    def fieldsets(self):
        self._fieldsets = [
            ('Kontaktujte nás',
             {'fields': ('from_email', 'subject', 'text'),
             'description': 'Ak máte akékoľvek otázky, pripomienky, alebo návrhy, neváhajte nás kontaktovať.', }),
        ]

        return super(ContactForm, self).fieldsets

    class Meta:
        model = Message

        help_texts = {
            'from_email': 'Váš e-mail, zašleme vám naň odpoveď.',
        }

        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }

        labels = {
            'from_email': 'E-mail',
            'subject': 'Predmet',
            'text': 'Správa',
        }

        exclude = ['send_time']
