from django.contrib import admin
from django.utils import timezone
from django.shortcuts import render
from django.urls import path

from .models import *


class IsExpiredFilter(admin.SimpleListFilter):
    title = 'expirované'
    parameter_name = 'expired'

    def lookups(self, request, model_admin):
        return (
            (True, 'Yes'),
            (False, 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value  == 'True':
            return queryset.exclude(expiration__gt=timezone.now())
        elif value == 'False':
            return queryset.filter(expiration__gt=timezone.now())

        return queryset


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'expiration')
    list_filter = (IsExpiredFilter, 'published')
    list_per_page = 100

    search_fields = ['title', 'description', 'description']
    ordering = ('-expiration', '-pk',)

    date_hierarchy = 'expiration'

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('title', 'published', 'expiration',),
            # 'description': 'optional description',
        }),
        ('Obsah', {
            'classes': ('wide',),
            'fields': ('description','image',),
            # 'description': 'optional description',
        }),
    )

    actions = [
        'expire',
        'publish'
    ]

    def expire(self, request, queryset):
        for q in queryset:
            q.expire_now()
    
    expire.short_description = 'Expiruj teraz'

    def publish(self, request, queryset):
        for q in queryset:
            q.publish()
    
    publish.short_description = 'Publikuj'


class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order')
    list_filter = ('published', 'category')
    list_per_page = 100

    search_fields = ['title', 'description']
    ordering = ('published', 'category', 'order')

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('title', 'published', 'category', 'order'),
            # 'description': 'optional description',
        }),
        ('Obsah', {
            'classes': ('wide',),
            'fields': ('description','image',),
            # 'description': 'optional description',
        }),
    )

    actions = [
        'publish',
    ]

    def publish(self, request, queryset):
        for q in queryset:
            q.publish()
    
    publish.short_description = 'Publikuj'


class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_email', 'send_time')
    list_filter = ('archived',)
    list_per_page = 100

    search_fields = ['from_email', 'subject', 'text']
    ordering = ('-send_time', '-pk')

    date_hierarchy = 'send_time'

    fieldsets = (
        ('Hlavička', {
            'classes': ('wide',),
            'fields': ('from_email', 'archived', 'subject'),
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

    actions = [
        'make_archived',
    ]

    def make_archived(self, request, queryset):
        for q in queryset:
            q.archive()
    
    make_archived.short_description = 'Archivuj'

    def changelist_view(self, request, extra_context=None):
        if 'archived__exact' not in request.GET:
            q = request.GET.copy()
            q['archived__exact'] = False
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(MessageAdmin, self).changelist_view(request, extra_context=extra_context)


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

    actions = [
        'end_organizing',
        'get_emails'
    ]

    def end_organizing(self, request, queryset):
        for q in queryset:
            q.end_now()

    end_organizing.short_description = 'Ukonči organizáciu'

    def get_emails(self, request, queryset):
        template = 'admin/org_email_list.html'

        context = dict(self.admin_site.each_context(request))
        context['orgs'] = queryset

        return render(request, template, context)
    
    get_emails.short_description = 'Zobraz kontakty'


admin.site.register(News, NewsAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(OrganizerProfile, OrganizerProfileAdmin)

admin.site.site_header = 'Stredoškolská liga Ultimate Frisbee'
admin.site.site_title = 'SLU'
admin.site.index_title = 'Organizácia'
