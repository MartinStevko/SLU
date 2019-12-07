from django.contrib import admin, messages
from django import forms
from django.urls import resolve
from django.shortcuts import redirect, render

from imagekit.admin import AdminThumbnail
from imagekit import ImageSpec
from imagekit.processors import ResizeToFill
from imagekit.cachefiles import ImageCacheFile

from .models import *
from registration.models import Player


class SeasonAdmin(admin.ModelAdmin):
    list_display = ('school_year', 'season', 'game_format')
    list_display_links = ('school_year',)
    list_filter = ('season',)
    list_per_page = 100

    search_fields = [
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

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if kwargs:
            t = Tournament.objects.get(
                pk=resolve(request.path_info).kwargs['object_id']
            )

            if db_field.name == 'team':
                kwargs['queryset'] = Team.objects.filter(
                    tournament=t,
                    confirmed=True
                )

        return super(ResultInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class MatchInline(admin.TabularInline):
    model = Match
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if kwargs:
            t = Tournament.objects.get(
                pk=resolve(request.path_info).kwargs['object_id']
            )

            if db_field.name in ['home_team', 'host_team']:
                kwargs['queryset'] = Team.objects.filter(
                    tournament=t,
                    confirmed=True
                )

        return super(MatchInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'season', 'date', 'place')
    list_display_links = ('__str__',)
    list_filter = ('state', 'season__season', 'region', 'player_stats')
    list_per_page = 100

    inlines = [MatchInline, ResultInline]

    search_fields = [
        'orgs__username',
        'orgs__first_name',
        'orgs__last_name',
        'delegate',
        'director',
        'institute'
    ]
    readonly_fields = ['state']
    ordering = ('-season__school_year', '-date', '-pk')

    # Autocomplete is other possibility, but I think filtering is better
    # autocomplete_fields = ['orgs']
    filter_horizontal = ['orgs', 'scorekeepers']

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
            'fields': ('director', 'institute', 'delegate', 'orgs', 'scorekeepers'),
            # 'description': 'optional description',
        }),
        ('Prílohy', {
            'classes': ('wide',),
            'fields': ('image', 'prop_image',),
            # 'description': 'optional description',
        }),
    )

    actions = [
        'get_contacts',
        'get_contacts_registered',
        'get_contacts_invited',
        'get_contacts_waitlisted',
        'get_email_list',
        'get_invited_email_list',
        'get_registered_email_list',
        'change_state_to_notpublic',
        'change_state_to_public',
        'change_state_to_registration',
        'change_state_to_active',
        'change_state_to_results',
        'send_last_info',
        'add_photos',
    ]

    def response_change(self, request, tournament):
        if '_save' in request.POST:
            return redirect('tournament:detail', pk=tournament.pk)
        else:
            return super().response_change(request, tournament)

    def get_contacts(self, request, queryset, condition=None):
        template = 'admin/tournament_contact_list.html'

        context = dict(self.admin_site.each_context(request))
        query_list = []
        for tournament in queryset:
            if condition is not None:
                team_queryset = Team.objects.filter(
                    status__in=condition,
                    tournament=tournament,
                )
            else:
                team_queryset = Team.objects.filter(
                    tournament=tournament,
                )
            teams = []
            for team in team_queryset:
                for item in STATUSES:
                    if item[0] == team.status:
                        status = item[1]
                if len(team.players.all()) > 0:
                    teams.append((team, True, status))
                else:
                    teams.append((team, False, status))
            query_list.append((tournament, teams))

        context['tournaments'] = query_list

        return render(request, template, context)

    get_contacts.short_description = 'Zobraziť všetky tímy'

    def get_contacts_registered(self, request, queryset):
        return self.get_contacts(
            request,
            queryset,
            condition=['registered', 'invited', 'waitlisted']
        )

    get_contacts_registered.short_description = 'Zobraziť registrované tímy'

    def get_contacts_invited(self, request, queryset):
        return self.get_contacts(
            request,
            queryset,
            condition=['invited']
        )

    get_contacts_invited.short_description = 'Zobraziť pozvané tímy'

    def get_contacts_waitlisted(self, request, queryset):
        return self.get_contacts(
            request,
            queryset,
            condition=['waitlisted']
        )

    get_contacts_waitlisted.short_description = 'Zobraziť tímy na čakacej listine'

    def get_email_list(self, request, queryset, condition=None):
        template = 'admin/tournament_email_list.html'

        context = dict(self.admin_site.each_context(request))
        contact_list = []
        for tournament in queryset:
            emails = []
            if condition is not None:
                teams = Team.objects.filter(
                    tournament=tournament,
                    status__in=condition,
                )
            else:
                teams = Team.objects.filter(
                    tournament=tournament,
                )
            for team in teams:
                for e in team.get_emails():
                    emails.append(e)
            contact_list.append((tournament, emails))
        context['contact_list'] = contact_list

        return render(request, template, context)

    get_email_list.short_description = 'E-maily na všetky tímy'

    def get_invited_email_list(self, request, queryset):
        return self.get_email_list(
            request,
            queryset,
            condition=['invited'],
        )

    get_invited_email_list.short_description = 'E-maily na pozvané tímy'

    def get_registered_email_list(self, request, queryset):
        return self.get_email_list(
            request,
            queryset,
            condition=['registered'],
        )

    get_registered_email_list.short_description = 'E-maily na tímy s nepotvrdenou registráciou'

    def change_state_to_notpublic(self, request, queryset):
        for q in queryset:
            if self.has_change_permission(request, q):
                q.change_state('not_public')
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Stav turnaja {} bol zmenený na neverejný.'.format(str(q))
                )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    '{} - Na túto akciu nemáte dostatočné oprávnenia.'.format(str(q))
                )

    change_state_to_notpublic.short_description = 'Spraviť turnaj neverejným'

    def change_state_to_public(self, request, queryset):
        for q in queryset:
            if self.has_change_permission(request, q):
                q.change_state('public')
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Stav turnaja {} bol zmenený na verejný. Turnaj čaká na otvorenie registrácie.'.format(str(q))
                )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    '{} - Na túto akciu nemáte dostatočné oprávnenia.'.format(str(q))
                )

    change_state_to_public.short_description = 'Spraviť turnaj verejným (registrácia neotvorená)'

    def change_state_to_registration(self, request, queryset):
        for q in queryset:
            if self.has_change_permission(request, q):
                q.change_state('registration')
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Registrácia turnaja {} bola otvorená.'.format(str(q))
                )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    '{} - Na túto akciu nemáte dostatočné oprávnenia.'.format(str(q))
                )

    change_state_to_registration.short_description = 'Otvoriť registráciu turnaja'

    def change_state_to_active(self, request, queryset):
        for q in queryset:
            if self.has_change_permission(request, q):
                if q.date - datetime.timedelta(days=1) <= datetime.date.today():
                    q.change_state('active')
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        'Turnaj {} bol otvorený.'.format(str(q))
                    )
                else:
                    messages.add_message(
                        request,
                        messages.WARNING,
                        'Turnaj {} nie je možné otvoriť, pretože dátum konania je priveľmi vzdialený.'.format(str(q))
                    )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    '{} - Na túto akciu nemáte dostatočné oprávnenia.'.format(str(q))
                )

    change_state_to_active.short_description = 'Začať turnaj'

    def change_state_to_results(self, request, queryset):
        for q in queryset:
            if self.has_change_permission(request, q):
                if q.date <= datetime.date.today():
                    msg = q.change_state('results')
                    if msg is not None:
                        messages.add_message(
                            request,
                            messages.WARNING,
                            msg
                        )
                    else:
                        messages.add_message(
                            request,
                            messages.SUCCESS,
                            'Výsledky turnaja {} boli zverejnené a odoslané tímom.'.format(str(q))
                        )
                else:
                    messages.add_message(
                        request,
                        messages.WARNING,
                        'Výsledky turnaja {} nie je možné zverejniť, pretože dátum konania ešte nenastal.'.format(str(q))
                    )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    '{} - Na túto akciu nemáte dostatočné oprávnenia.'.format(str(q))
                )

    change_state_to_results.short_description = 'Zverejniť výsledky turnaja'

    def send_last_info(self, request, queryset):
        for q in queryset:
            teams = Team.objects.filter(
                tournament=t,
                status='invited',
            )

            for team in teams:
                matches = []
                for m in Match.objects.filter(tournament=q):
                    if m.home_team == team or m.host_team == team:
                        matches.append(m)

                SendMail(
                    team.get_emails(),
                    str(q),
                ).last_info_email(
                    team,
                    matches,
                )
    
    send_last_info.short_description = 'Polať pozvaným tímom posledné informácie'

    def add_photos(self, request, queryset):
        return redirect('admin:tournament_abstractgallery_add')
    
    add_photos.short_description = 'Pridať fotky'

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.orgs.all():
                return True

        return request.user.has_perm('tournament.change_tournament')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.orgs.all():
                return True

        return request.user.has_perm('tournament.delete_tournament')


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

    actions = [
        'get_contacts',
        'invite',
        'make_attended',
        'cancel_registration',
        'make_not_attended',
    ]

    def response_change(self, request, team):
        if '_save' in request.POST and request.session.get('checkin', False):
            return redirect('tournament:team_checkin', pk=team.tournament.pk, team=team.pk)
        else:
            return super().response_change(request, team)

    def make_attended(self, request, queryset):
        for q in queryset:
            if request.user.is_superuser or \
                request.user.has_perm('team.change_team') or \
                    (q in Team.objects.filter(
                        tournament__in=request.user.tournament_set.all()
                    )):
                msg, tag = q.attend()
                messages.add_message(request, tag, msg)
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'Na túto akciu nemáte dostatočné oprávnenia.'
                )

    make_attended.short_description = 'Označiť ako zúčastnený'

    def make_not_attended(self, request, queryset):
        for q in queryset:
            if request.user.is_superuser or \
                request.user.has_perm('team.change_team') or \
                    (q in Team.objects.filter(
                        tournament__in=request.user.tournament_set.all()
                    )):
                msg, tag = q.not_attend()
                messages.add_message(request, tag, msg)
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'Na túto akciu nemáte dostatočné oprávnenia.'
                )

    make_not_attended.short_description = 'Označiť ako nezúčastnený'
    
    def invite(self, request, queryset):
        for q in queryset:
            if request.user.is_superuser or \
                request.user.has_perm('team.change_team') or \
                    (q in Team.objects.filter(
                        tournament__in=request.user.tournament_set.all()
                    )):
                msg, tag = q.invite()
                messages.add_message(request, tag, msg)
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'Na túto akciu nemáte dostatočné oprávnenia.'
                )

    invite.short_description = 'Pozvať na turnaj'

    def cancel_registration(self, request, queryset):
        for q in queryset:
            if request.user.is_superuser or \
                request.user.has_perm('team.change_team') or \
                    (q in Team.objects.filter(
                        tournament__in=request.user.tournament_set.all()
                    )):
                msg, tag = q.cancel()
                messages.add_message(request, tag, msg)
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'Na túto akciu nemáte dostatočné oprávnenia.'
                )

    cancel_registration.short_description = 'Odmietnuť vybrané tímy'

    def get_contacts(self, request, queryset):
        template = 'admin/team_contact_list.html'

        context = dict(self.admin_site.each_context(request))
        teams = []
        for team in queryset:
            for item in STATUSES:
                if item[0] == team.status:
                    status = item[1]
            if len(team.players.all()) > 0:
                teams.append((team, True, status))
            else:
                teams.append((team, False, status))
        context['teams'] = teams

        return render(request, template, context)

    get_contacts.short_description = 'Zobraziť kontakty'

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.change_team')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.delete_team')


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

    date_hierarchy = 'tournament__date'

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

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.change_result')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.delete_result')


class SpiritScoreAdmin(admin.ModelAdmin):
    list_per_page = 100

    search_fields = [
        'tournament',
        'from_team__name',
        'from_team__school__name',
        'to_team__name',
        'to_team__school__name',
    ]
    ordering = ('-pk',)

    date_hierarchy = 'tournament__date'

    fieldsets = (
        ('Zápas', {
            'classes': ('wide',),
            'fields': ('tournament', ('from_team', 'to_team')),
        }),
        ('Body', {
            'classes': ('wide',),
            'fields': (('rules', 'fouls', 'fair'), ('selfcontrol', 'communication')),
        }),
        ('Poznámka', {
            'classes': ('wide',),
            'fields': ('note',),
        }),
    )

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.change_result')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.delete_result')


class PointInline(admin.TabularInline):
    model = Point
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if kwargs:
            m = Match.objects.get(
                pk=resolve(request.path_info).kwargs['object_id']
            )

            if db_field.name in ['score', 'assist']:
                kwargs['queryset'] = Player.objects.filter(
                    team__in=[m.home_team, m.host_team],
                )

        return super(PointInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class MatchAdminForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(MatchAdminForm, self).__init__(*args, **kwargs)

        try:
            ins = self.instance.tournament
        except:
            pass
        else:
            if ins:
                self.fields['home_team'].queryset = Team.objects.filter(tournament=ins)
                self.fields['host_team'].queryset = Team.objects.filter(tournament=ins)


class MatchAdmin(admin.ModelAdmin):
    form = MatchAdminForm

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

    date_hierarchy = 'tournament__date'

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

    def response_change(self, request, match):
        if '_save' in request.POST:
            return redirect('tournament:match_detail', pk=match.pk)
        else:
            return super().response_change(request, match)

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True
            
            if request.user in obj.tournament.scorekeepers.all():
                return True

        return request.user.has_perm('tournament.change_match')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.delete_match')


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

    date_hierarchy = 'match__tournament__date'

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

    def response_change(self, request, point):
        if '_save' in request.POST:
            return redirect('tournament:match_detail', pk=point.match.pk)
        else:
            return super().response_change(request, point)

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.match.tournament.orgs.all():
                return True
            
            if request.user in obj.match.tournament.scorekeepers.all():
                return True

        return request.user.has_perm('tournament.change_point')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.match.tournament.orgs.all():
                return True

            if request.user in obj.match.tournament.scorekeepers.all():
                return True

        return request.user.has_perm('tournament.delete_point')


class AdminThumbnailSpec(ImageSpec):
    processors = [ResizeToFill(100, 75)]
    format = 'JPEG'
    options = {'quality': 60 }


def cached_admin_thumb(instance):
    cached = ImageCacheFile(AdminThumbnailSpec(instance.image))
    cached.generate()
    return cached


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tournament', 'admin_thumbnail')
    admin_thumbnail = AdminThumbnail(image_field=cached_admin_thumb)
    list_display_links = ('pk',)
    list_filter = (
        'tournament__season__season',
        'tournament__region',
        'tournament__season__school_year'
    )
    list_per_page = 100

    search_fields = ['pk',]
    ordering = ('-pk',)

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.change_photo')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('tournament.delete_photo')


class AbstractGalleryAdmin(admin.ModelAdmin):
    list_filter = (
        'tournament__season__season',
        'tournament__region',
        'tournament__season__school_year'
    )
    list_per_page = 100

    ordering = ('-pk',)

    date_hierarchy = 'tournament__date'

    fieldsets = (
        ('Galéria', {
            'classes': ('wide',),
            'fields': ('tournament', 'zip_file'),
        }),
    )

    def response_add(self, request, obj):
        messages.add_message(
            request,
            messages.SUCCESS,
            'Fotky zo súboru ZIP boli úspešne importované.'
        )
        return redirect('admin:tournament_tournament_changelist')


admin.site.register(Season, SeasonAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(SpiritScore, SpiritScoreAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(AbstractGallery, AbstractGalleryAdmin)
