from django.contrib import admin

from emails.models import *
from emails.emails import SendMail


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
    ]

    def test_send(self, request, queryset):
        for q in queryset:
            SendMail(
                [request.user.email],
                'Test - '+q.subject,
            ).test_mail(q.tag)
    
    test_send.short_description = 'Poslať skúšobný e-mail'

    def test_creation(self, request, queryset):
        SendMail(
            [request.user.email],
            'Vytvorenie konta'
        ).user_creation(request.user)
    
    test_creation.short_description = 'Poslať skúšobný e-mail o vytvorení konta'


admin.site.register(Template, TemplateAdmin)
