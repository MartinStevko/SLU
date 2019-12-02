from django.contrib import admin, messages
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from emails.emails import SendMail
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    list_per_page = 100

    search_fields = [
        'first_name',
        'last_name',
        'email',
    ]
    ordering = ('-pk',)

    filter_horizontal = ['groups', 'user_permissions']

    readonly_fields = ('password_expiration', 'last_login')

    fieldsets = (
        ('Prihlásenie', {
            'classes': ('wide',),
            'fields': ('email', 'password_expiration', 'last_login'),
        }),
        ('Osoba', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
        ('Oprávnenia', {
            'classes': ('wide',),
            'fields': ('is_staff', 'is_central_org', 'is_superuser', 'groups'),
        }), 
        ('Extra oprávnenia', {
            'classes': ('collapse',), 
            'fields': ('user_permissions',), 
            'description': 'Za normálnych okolností sa neudeľujú a mali by vystačiť '+\
                'skupiny oprávnení, avšak pre nejaké špeciálne potreby môžu byť '+\
                    'využité. Priraďujú oprávnenia nad rámec skupín. '
        }), 
    )

    actions = [
        'send_creation_email',
    ]

    def send_creation_email(self, request, queryset):
        if request.user.has_perm('user.send_creation_email'):
            for q in queryset:
                SendMail(
                    [q.email],
                    'Vytvorenie konta'
                ).user_creation(q)
            
            messages.add_message(request, messages.SUCCESS, 'E-maily boli úspešne odoslané.')
        else:
            messages.add_message(request, messages.WARNING, 'Na túto akciu nemáte oprávnenie.')

    send_creation_email.short_description = 'Poslať e-mail o vytvorení účtu'


admin.site.register(User, UserAdmin)
admin.site.register(Permission)