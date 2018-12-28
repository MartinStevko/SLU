from django.contrib import admin

from .models import *


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'expiration')
    list_per_page = 100

    search_fields = ['title', 'description']
    ordering = ('-expiration', '-pk',)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('category', 'title')
    list_filter = ('category',)
    list_per_page = 100

    search_fields = ['title', 'description']
    ordering = ('-pk',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_email', 'send_time', 'subject')
    list_per_page = 100

    search_fields = ['from_email', 'subject', 'text']
    ordering = ('-send_time', '-pk')


class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'start_season', 'end_season')
    list_filter = ('start_season', 'end_season')
    list_per_page = 100

    search_fields = ['full_name', 'email']
    ordering = ('-pk',)


admin.site.register(News, NewsAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(OrganizerProfile, OrganizerProfileAdmin)

admin.site.site_header = 'Stredoškolská liga Ultimate Frisbee'
admin.site.site_title = 'SLU'
admin.site.index_title = 'Organizácia'
