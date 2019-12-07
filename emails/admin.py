from django.contrib import admin, messages

from emails.models import *
from emails.emails import SendMail

from emails.tests import CustomTeam, CustomMatch


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('subject', 'text')
    list_filter = ('tag',)

    search_fields = ['subject', 'text', 'html']
    ordering = ('-pk',)

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('subject', 'tag',),
        }),
        ('Telo', {
            'classes': ('wide',),
            'fields': ('text','html',),
        }),
    )

    actions = [
        'test_send',
        'test_creation',
        'test_registration_open',
        'test_last_info_email',
    ]

    def test_send(self, request, queryset):
        if request.user.email:
            for q in queryset:
                SendMail(
                    [request.user.email],
                    'Test - '+q.subject,
                ).test_mail(q.tag)

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Testovací e-mail "{}", bol odoslaný na váš e-mail.'.format(q.subject)
                )
        else:
            messages.add_message(
                request,
                messages.WARNING,
                'E-mail sa nepodarilo odoslať. Vyplňte mailovú adresu '+\
                    'vo vašom účte a akciu opakujte.'
            )

    test_send.short_description = 'Poslať skúšobný e-mail'

    def test_creation(self, request, queryset):
        if request.user.email:
            SendMail(
                [request.user.email],
                'Vytvorenie konta'
            ).user_creation(request.user)

            messages.add_message(
                request,
                messages.SUCCESS,
                'Testovací e-mail bol odoslaný na váš e-mail.'
            )
        else:
            messages.add_message(
                request,
                messages.WARNING,
                'E-mail sa nepodarilo odoslať. Vyplňte mailovú adresu '+\
                    'vo vašom účte a akciu opakujte.'
            )
    
    test_creation.short_description = 'Poslať skúšobný e-mail - vytvorenie konta'

    def test_registration_open(self, request, queryset):
        if request.user.email:
            SendMail(
                [request.user.email],
                'Skúška - Meno turnaja'
            ).registration_open_notification(1)

            messages.add_message(
                request,
                messages.SUCCESS,
                'Testovací e-mail bol odoslaný na váš e-mail.'
            )
        else:
            messages.add_message(
                request,
                messages.WARNING,
                'E-mail sa nepodarilo odoslať. Vyplňte mailovú adresu '+\
                    'vo vašom účte a akciu opakujte.'
            )
    
    test_registration_open.short_description = 'Poslať skúšobný e-mail - otvorenie registrácie'

    def test_last_info_email(self, request, queryset):
        if request.user.email:
            SendMail(
                [request.user.email],
                'Skúška - Meno turnaja'
            ).last_info_email(
                CustomTeam(),
                [CustomMatch, CustomMatch],
            )

            messages.add_message(
                request,
                messages.SUCCESS,
                'Testovací e-mail bol odoslaný na váš e-mail.'
            )
        else:
            messages.add_message(
                request,
                messages.WARNING,
                'E-mail sa nepodarilo odoslať. Vyplňte mailovú adresu '+\
                    'vo vašom účte a akciu opakujte.'
            )
    
    test_last_info_email.short_description = 'Poslať skúšobný e-mail - tímový checkin'


class GenericAdmin(admin.ModelAdmin):
    list_display = ('name', 'pdf')
    list_filter = ('doc_type',)

    search_fields = ['name',]
    ordering = ('-time_created', '-pk',)

    date_hierarchy = 'time_created'

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('name', 'doc_type',),
        }),
        ('Súbor', {
            'classes': ('wide',),
            'fields': ('pdf',),
        }),
    )


admin.site.register(Template, TemplateAdmin)
admin.site.register(Generic, GenericAdmin)
