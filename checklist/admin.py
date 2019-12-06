from django.contrib import admin, messages

from checklist.models import *


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 100

    search_fields = [
        'name',
    ]
    ordering = ('-pk',)

    fieldsets = (
        ('Dokument', {
            'classes': ('wide',),
            'fields': ('name', 'document'),
        }),
    )


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('phase',)
    list_per_page = 100

    search_fields = [
        'name',
        'description',
    ]
    ordering = ('phase', '-pk')

    fieldsets = (
        ('Úloha', {
            'classes': ('wide',),
            'fields': (('name', 'phase'), 'description'),
        }),
    )


class TaskStatusInline(admin.TabularInline):
    model = TaskStatus
    extra = 3

    autocomplete_fields = ['task']


class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    list_per_page = 100

    inlines = [TaskStatusInline]

    search_fields = [
        'tournament',
    ]
    ordering = ('-tournament__date', '-pk')

    autocomplete_fields = ['tournament']

    date_hierarchy = 'tournament__date'

    fieldsets = (
        ('Zoznam úloh', {
            'classes': ('wide',),
            'fields': ('tournament',),
        }),
    )

    actions = [
        'clone_new',
    ]

    def clone_new(self, request, queryset):
        for q in queryset:
            tasks = TaskStatus.objects.filter(checklist=q)
            ch = Checklist.objects.create()
            ch.save()
            for task in tasks:
                task.duplicate(ch)
            
            messages.add_message(
                request,
                messages.SUCCESS,
                'Bola vytvorená kópia zoznamu úloh - {}.'.format(q)
            )

    clone_new.short_description = 'Vytvoriť kópiu úloh'

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('checklist.change_checklist')

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:
                return True

            if request.user in obj.tournament.orgs.all():
                return True

        return request.user.has_perm('checklist.delete_checklist')

    def response_add(self, request, obj):
        if not obj.tournament:
            messages.add_message(
                request,
                messages.WARNING,
                'Checklist nemá zvolený turnaj, slúži teda '+\
                    'iba ako šablóna a nebude sa nikde zobrazovať.'
            )
        
        return super().response_add(request, obj)

    def response_change(self, request, obj):
        if not obj.tournament:
            messages.add_message(
                request,
                messages.WARNING,
                'Checklist nemá zvolený turnaj, slúži teda '+\
                    'iba ako šablóna a nebude sa nikde zobrazovať.'
            )
        
        return super().response_change(request, obj)


admin.site.register(Document, DocumentAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Checklist, ChecklistAdmin)
