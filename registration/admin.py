from django.contrib import admin
from django.shortcuts import render

from .models import *


class TeacherInline(admin.TabularInline):
    model = Teacher
    extra = 0

    can_delete = False


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'city', 'web')
    list_display_links = ('name',)
    list_filter = ('region', 'have_disc')
    list_per_page = 100

    inlines = [TeacherInline]

    search_fields = ['name', 'street', 'city']
    ordering = ('-pk',)

    fieldsets = (
        ('Základné informácie', {
            'classes': ('wide',),
            'fields': ('name', 'web', 'have_disc'),
            # 'description': 'optional description',
        }),
        ('Adresa', {
            'classes': ('wide',),
            'fields': ('street', 'postcode', ('city', 'region')),
            # 'description': 'optional description',
        }),
    )

    actions = [
        'get_emails',
        'get_info',
        'get_players'
    ]

    def get_emails(self, request, queryset):
        template = 'admin/teacher_contact_list.html'

        context = dict(self.admin_site.each_context(request))
        context['teachers'] = Teacher.objects.filter(school__in=queryset)
        context['email'] = True

        return render(request, template, context)

    get_emails.short_description = 'Zobraz e-maily'

    def get_info(self, request, queryset):
        template = 'admin/school_info_list.html'

        context = dict(self.admin_site.each_context(request))
        context['schools'] = queryset
        context['email'] = True

        return render(request, template, context)

    get_info.short_description = 'Zobraz základné informácie'

    def get_players(self, request, queryset):
        template = 'admin/school_players_list.html'

        context = dict(self.admin_site.each_context(request))
        players = []
        for s in queryset:
            players.append(Player.objects.filter(school=s).order_by(
                'last_name',
                'first_name',
            ))

        context['schools'] = zip(queryset, players)
        context['email'] = True

        return render(request, template, context)

    get_players.short_description = 'Zobraz hráčov'


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'school')
    list_display_links = ('first_name',)
    list_filter = ('school__region',)
    list_per_page = 100

    search_fields = [
        'first_name',
        'last_name',
        'email',
        'school__name',
        'school__street',
        'school__city'
    ]
    ordering = ('-pk',)

    fieldsets = (
        ('Základné informácie', {
            'classes': ('wide',),
            'fields': ('school', ('first_name', 'last_name')),
            # 'description': 'optional description',
        }),
        ('Kontakt', {
            'classes': ('wide',),
            'fields': ('email', 'phone_number'),
            # 'description': 'optional description',
        }),
    )

    actions = [
        'get_emails',
        'get_phone_numbers'
    ]

    def get_emails(self, request, queryset):
        return self.get_contacts(request, queryset, True)

    get_emails.short_description = 'Zobraz e-maily'

    def get_phone_numbers(self, request, queryset):
        return self.get_contacts(request, queryset, False)

    get_phone_numbers.short_description = 'Zobraz telefóonne čísla'

    def get_contacts(self, request, queryset, email):
        template = 'admin/teacher_contact_list.html'

        context = dict(self.admin_site.each_context(request))
        context['teachers'] = queryset
        context['email'] = email

        return render(request, template, context)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'school')
    list_display_links = ('first_name',)
    list_filter = ('sex', 'school__region')
    list_per_page = 100

    search_fields = [
        'first_name',
        'last_name',
        'school__name',
        'school__street',
        'school__city'
    ]
    ordering = ('-pk',)

    radio_fields = {'sex': admin.HORIZONTAL}

    fieldsets = (
        ('Základné informácie', {
            'classes': ('wide',),
            'fields': ('school', ('first_name', 'last_name')),
            # 'description': 'Základné informácie o hráčovi',
        }),
        ('Turnajové štatistiky', {
            'classes': ('wide',),
            'fields': ('sex', 'is_exception'),
            # 'description': 'Informácie potrebné na \
            # generovanie štatistík a rebríčku hráčov',
        }),
    )

admin.site.register(School, SchoolAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Player, PlayerAdmin)
