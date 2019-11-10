from django.contrib import admin

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
