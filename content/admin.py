from django.contrib import admin

from .models import *


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'expiration')
    list_per_page = 100

    search_fields = ['title', 'description']
    ordering = ('-expiration', '-pk',)

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('title', 'expiration',),
            # 'description': 'optional description',
        }),
        ('Obsah', {
            'classes': ('wide',),
            'fields': ('description','image',),
            # 'description': 'optional description',
        }),
    )


class SectionAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'order')
    list_filter = ('category',)
    list_per_page = 100

    search_fields = ['title', 'description']
    ordering = ('-pk',)

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('title', 'category', 'order'),
            # 'description': 'optional description',
        }),
        ('Obsah', {
            'classes': ('wide',),
            'fields': ('description','image',),
            # 'description': 'optional description',
        }),
    )


class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_email', 'send_time')
    list_per_page = 100

    search_fields = ['from_email', 'subject', 'text']
    ordering = ('-send_time', '-pk')

    date_hierarchy = 'send_time'

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('from_email', 'subject'),
            # 'description': 'optional description',
        }),
        ('Podrobné informácie', {
            'classes': ('collapse',),
            'fields': ('send_time',),
            # 'description': 'optional description',
        }),
        ('Obsah', {
            'classes': ('wide',),
            'fields': ('text',),
            # 'description': 'optional description',
        }),
    )


class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'start_season', 'end_season')
    list_filter = ('start_season', 'end_season')
    list_per_page = 100

    search_fields = ['full_name', 'email']
    ordering = ('-pk',)

    fieldsets = (
        ('Základné infromácie', {
            'classes': ('wide',),
            'fields': ('full_name', 'email'),
            # 'description': 'optional description',
        }),
        ('Obsah', {
            'classes': ('wide',),
            'fields': ('image', ('start_season', 'end_season')),
            # 'description': 'optional description',
        }),
    )


admin.site.register(News, NewsAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(OrganizerProfile, OrganizerProfileAdmin)

admin.site.site_header = 'Stredoškolská liga Ultimate Frisbee'
admin.site.site_title = 'SLU'
admin.site.index_title = 'Organizácia'
