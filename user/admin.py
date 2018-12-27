from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class EmailRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)
        # make user email field required
        self.fields['email'].required = True


class OrganizerCreationForm(EmailRequiredMixin, UserCreationForm):
    pass


class OrganizerChangeForm(EmailRequiredMixin, UserChangeForm):
    pass


class EmailRequiredUserAdmin(UserAdmin):
    form = OrganizerChangeForm
    add_form = OrganizerCreationForm
    add_fieldsets = ((None, {
        'fields': ('username', 'email', 'password1', 'password2'), 
        'classes': ('wide',)
    }),)

admin.site.unregister(User)
admin.site.register(User, EmailRequiredUserAdmin)
