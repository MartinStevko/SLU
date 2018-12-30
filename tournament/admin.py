from django.contrib import admin

from .models import *


class SeasonAdmin(admin.ModelAdmin):
    list_display = ('school_year', 'season', 'game_format')
    list_display_links = ('school_year',)
    list_filter = ('season',)
    list_per_page = 100

    search_fields = [
        'orgs__username',
        'orgs__first_name',
        'orgs__last_name',
    ]
    ordering = ('-school_year', '-pk')

    # Autocomplete is other possibility, but I think filtering is better
    # autocomplete_fields = ['orgs']
    filter_horizontal = ['orgs']

    radio_fields = {'season': admin.HORIZONTAL}

    fieldsets = (
        ('Nastavenia', {
            'classes': ('wide',),
            'fields': ('school_year', 'season', 'game_format'),
            # 'description': 'optional description',
        }),
        ('Centrálna organizácia', {
            'classes': ('wide',),
            'fields': ('orgs',),
            # 'description': 'optional description',
        }),
    )


class ResultInline(admin.TabularInline):
    model = Result
    extra = 0

    can_delete = False


class MatchInline(admin.TabularInline):
    model = Match
    extra = 1

    exclude = ['begining_time']


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('season', 'date', 'place')
    list_display_links = ('season',)
    list_filter = ('state', 'season__season', 'region', 'player_stats')
    list_per_page = 100

    inlines = [ResultInline, MatchInline]

    search_fields = [
        'orgs__username',
        'orgs__first_name',
        'orgs__last_name',
        'delegate',
        'director',
        'institute'
    ]
    ordering = ('-season__school_year', '-date', '-pk')

    # Autocomplete is other possibility, but I think filtering is better
    # autocomplete_fields = ['orgs']
    filter_horizontal = ['orgs']

    date_hierarchy = 'date'

    fieldsets = (
        ('Základné informácie', {
            'classes': ('wide',),
            'fields': ('place', 'in_city', 'date', 'signup_deadline'),
            # 'description': 'optional description',
        }),
        ('Systémové informácie', {
            'classes': ('wide',),
            'fields': ('season', 'region', 'state'),
            # 'description': 'optional description',
        }),
        ('Nastavenia', {
            'classes': ('wide',),
            'fields': (
                'game_duration',
                'cap',
                'max_teams',
                'number_qualified',
                'player_stats',
            ),
            # 'description': 'optional description',
        }),
        ('Harmonogram', {
            'classes': ('wide',),
            'fields': ('arrival_time', 'meeting_time', 'game_time', 'end_time',),
            # 'description': 'optional description',
        }),
        ('Lokálna organizácia', {
            'classes': ('wide',),
            'fields': ('director', 'institute', 'delegate', 'orgs',),
            # 'description': 'optional description',
        }),
        ('Prílohy', {
            'classes': ('wide',),
            'fields': ('image', 'prop_image',),
            # 'description': 'optional description',
        }),
    )


class TeamAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'school', 'teacher', 'status')
    list_display_links = ('school',)
    list_filter = (
        'tournament__season__season',
        'tournament__region',
        'status',
        'confirmed',
        'accept_gdpr'
    )
    list_per_page = 100

    search_fields = [
        'players__first_name',
        'players__last_name',
        'teacher__first_name',
        'teacher__last_name',
        'name',
        'school__name',
        'school__street',
        'school__city'
    ]
    ordering = ('name', '-pk')

    # Autocomplete is other possibility, but I think filtering is better
    # autocomplete_fields = ['players']
    filter_horizontal = ['players']

    fieldsets = (
        ('Turnaj', {
            'classes': ('collapse',),
            'fields': ('tournament',),
            # 'description': 'optional description',
        }),
        ('Základné informácie', {
            'classes': ('wide',),
            'fields': ('school', 'name',),
            # 'description': 'optional description',
        }),
        ('Stav', {
            'classes': ('wide',),
            'fields': ('status', 'confirmed', 'accept_gdpr',),
            # 'description': 'optional description',
        }),
        ('Súpiska', {
            'classes': ('wide',),
            'fields': ('teacher', 'players',),
            # 'description': 'optional description',
        }),
    )


class ResultAdmin(admin.ModelAdmin):
    list_filter = (
        'place',
    )
    list_per_page = 100

    search_fields = [
        'team__players__first_name',
        'team__players__last_name',
        'team__teacher__first_name',
        'team__teacher__last_name',
        'team__name',
        'team__school__name',
        'team__school__street',
        'team__school__city'
    ]
    ordering = (
        '-tournament__season__school_year',
        '-tournament__season__season',
        'place',
        '-pk'
    )

    fieldsets = (
        ('Turnaj', {
            'classes': ('collapse',),
            'fields': ('tournament',),
            # 'description': 'optional description',
        }),
        ('Výsledok', {
            'classes': ('wide',),
            'fields': (('place', 'team'),),
            # 'description': 'optional description',
        }),
    )


class PointInline(admin.TabularInline):
    model = Point
    extra = 0


class MatchAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'home_team', 'host_team', 'begining_time',)
    list_display_links = ('tournament',)
    list_filter = (
        'tournament__season__season',
        'tournament__region',
        'tournament__season__school_year'
    )
    list_per_page = 100

    inlines = [PointInline]

    search_fields = ['home_team', 'host_team']
    ordering = ('-pk',)

    date_hierarchy = 'begining_time'

    fieldsets = (
        ('Turnajové nastavenie', {
            'classes': ('collapse',),
            'fields': ('tournament', 'begining_time'),
            # 'description': 'optional description',
        }),
        ('Zápas', {
            'classes': ('wide',),
            'fields': (('home_team', 'host_team',),),
            # 'description': 'optional description',
        }),
    )


class PointAdmin(admin.ModelAdmin):
    list_display = ('time', 'match')
    list_display_links = ('time',)
    list_filter = (
        'match__tournament__season__season',
        'match__tournament__region',
        'match__tournament__season__school_year'
    )
    list_per_page = 100

    search_fields = ['score', 'assist']
    ordering = ('-pk',)

    fieldsets = (
        ('Zápas', {
            'classes': ('wide',),
            'fields': ('match', 'time'),
            # 'description': 'optional description',
        }),
        ('Bodovanie', {
            'classes': ('wide',),
            'fields': (('score', 'assist',),),
            # 'description': 'optional description',
        }),
    )


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tournament')
    list_display_links = ('pk',)
    list_filter = (
        'tournament__season__season',
        'tournament__region',
        'tournament__season__school_year'
    )
    list_per_page = 100

    search_fields = ['pk',]
    ordering = ('-pk',)

admin.site.register(Season, SeasonAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Photo, PhotoAdmin)
