from django.contrib import admin

from .models import *


class SeasonAdmin(admin.ModelAdmin):
    list_display = ('school_year', 'season', 'game_format')
    list_filter = ('season',)
    list_per_page = 100

    search_fields = [
        'orgs__username',
        'orgs__first_name',
        'orgs__last_name',
    ]
    ordering = ('-school_year', '-pk')


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('season', 'date', 'place')
    list_filter = ('season__season', 'region', 'player_stats')
    list_per_page = 100

    search_fields = [
        'orgs__username',
        'orgs__first_name',
        'orgs__last_name',
        'delegate',
        'director',
        'institute'
    ]
    ordering = ('-season__school_year', '-date', '-pk')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'school', 'teacher')
    list_filter = (
        'tournament__season__season',
        'tournament__region',
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


class MatchInline(admin.StackedInline):
    model = TeamInMatchRegistration
    extra = 0


class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'begining_time', 'tournament')
    list_filter = (
        'tournament__season__season',
        'tournament__region',
        'tournament__season__school_year'
    )
    list_per_page = 100

    inlines = [MatchInline]

    ordering = ('-pk',)


class PointInline(admin.TabularInline):
    model = PlayerInPoint
    extra = 0


class PointAdmin(admin.ModelAdmin):
    list_display = ('time', 'match')
    list_filter = (
        'match__tournament__season__season',
        'match__tournament__region',
        'match__tournament__season__school_year'
    )
    list_per_page = 100

    inlines = [PointInline]

    ordering = ('-pk',)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tournament')
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
