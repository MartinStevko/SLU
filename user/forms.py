from django import forms

from app.mixins import OverwriteOnlyModelFormMixin
from .models import User

class LoginForm(OverwriteOnlyModelFormMixin, forms.Form):
    email = forms.EmailField(
        empty_value='Používateľský email'
    )

    def clean(self):
        email = self.cleaned_data['email']

        try:
            User.objects.get(email=email)
        except(User.DoesNotExist):
            raise forms.ValidationError('Používateľ s touto emailovou adresou neexistuje.')
