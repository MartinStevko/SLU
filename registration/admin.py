from django.contrib import admin

from .models import *


class TeacherInline(admin.TabularInline):
    model = Teacher
    extra = 0

    exclude = ['email_verified']
    can_delete = False


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'city', 'web')
    list_filter = ('region',)
    list_per_page = 100

    inlines = [TeacherInline]

    search_fields = ['name', 'street', 'city']
    ordering = ('-pk',)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'school')
    list_filter = ('email_verified', 'school__region')
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


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'school')
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

admin.site.register(School, SchoolAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Player, PlayerAdmin)
