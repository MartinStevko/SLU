from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, render_to_response

from .models import *


class TeamAdmin(admin.ModelAdmin):
    list_display = ('meno', 'hraci', 'region', 'skola', 'adresa')
    list_filter = ('kvalifikovany', 'region', 'kraj')
    list_per_page = 100
    search_fields = ('meno', 'skola')
    ordering = ('-pk',)

    def hraci(self, team):
        players = Player.objects.filter(tim=team)
        return len(players)

    # Renames column head
    hraci.short_description = 'Počet hráčov'

    actions = [
        'basic_info',
        'get_team_songs',
        'get_posts',
        'get_invitations',
        'get_confirmations',
        'get_diplomas',
        'make_qualified'
    ]

    def make_qualified(self, request, queryset):
        rows_updated = queryset.update(kvalifikovany=True)
        if rows_updated == 1:
            message_bit = '1 tím bol označený ako kvalifikovaný'
        else:
            message_bit = '%s tímov bolo označených ako kvalifikované' % rows_updated
    make_qualified.short_description = 'Označiť vybrané tímy ako kvalifikované'

    def basic_info(self, request, queryset):
        teams_len = len(queryset)

        participants_len = 0

        mans = 0
        womans = 0

        m_bagets = 0
        v_bagets = 0
        n_bagets = 0

        captains = []
        teachers = []

        final = True
        for team in queryset:
            captains.append(team.mail)
            teachers.append(team.ucitel.mail)

            if not team.kvalifikovany:
                final = False

        for team in queryset:
            if final:
                participants = FinalMember.objects.filter(tim=team)
            else:
                participants = Player.objects.filter(tim=team)
            participants_len += len(participants)

            for partcp in participants:
                if partcp.pohlavie == 'W':
                    womans += 1
                else:
                    mans += 1
                
                if partcp.bageta == 'M':
                    m_bagets += 1
                elif partcp.bageta == 'V':
                    v_bagets += 1
                else:
                    n_bagets += 1

        c_contact = ''
        for captain in captains:
            c_contact += str(captain) + ','
        c_contact = c_contact[:-1]

        t_contact = ''
        for teacher in teachers:
            t_contact += str(teacher) + ','
        t_contact = t_contact[:-1]

        response = render_to_response('admin/statistics.html', {
            't': teams_len,
            'h': participants_len,
            'm': mans,
            'd': womans,
            'ma': m_bagets,
            've': v_bagets,
            'no': n_bagets,
            'captains': c_contact,
            'teachers': t_contact,
            'final': True,
        })

        return HttpResponse(response)
    basic_info.short_description = 'Štatistiky a kontakt'

    def get_team_songs(self, request, queryset):
        songs = '<body style="padding:20px;">'
        for team in queryset:
            songs += '<p>{}: <a href="{}">{}</a></p>'.format(team.meno, str(team.pesnicka), str(team.pesnicka))
        return HttpResponse(songs+'</body>')
    get_team_songs.short_description = 'Pozrieť tímové pesničky'

    def get_posts(self, request, queryset):
        posts = '<body style="padding:20px;">'
        for team in queryset:
            if team.sprava:
                posts += '<p>{}: {}</p>'.format(team.meno, team.sprava)

        if not len(posts) > 28:
            return HttpResponse(posts+'Nenašli sa žiadne správy. </body>')
        else:
            return HttpResponse(posts+'</body>')
    get_posts.short_description = 'Pozrieť správy'

    def get_diplomas(self, request, queryset):
        response = '<body style="padding: 20px;">'
        for team in queryset:
            response += '\\diplom{' + str(team.diplom_meno) + '}<br>'
        
        for i in range(len(queryset)//5):
            response += '\\diplomPrazdny<br>'
        for i in range(3):
            response += '\\spirit<br>'

        return HttpResponse(response+'</body>')
    get_diplomas.short_description = 'Generovať diplomy'

    def get_invitations(self, request, queryset):
        response = '<body style="padding: 20px;">'
        for team in queryset:
            response += '<p>\\tim{' + str(team.diplom_meno) + '}<br>' + \
            '\\skola{' + str(team.skola) + '}</p>'
        return HttpResponse(response+'</body>')
    get_invitations.short_description = 'Generovať pozvánky'

    def get_confirmations(self, request, queryset):
        c = '<body style="padding: 20px">'
        for team in queryset:
            c += '\\potvrdenka{%s}{%s}{%%' % (team.skola, team.ucitel.meno)

            players = Player.objects.filter(tim=team)
            for i in range(len(players)):
                c += '<br>%s.& %s \\\\ \\hline' % (str(i+1), players[i].meno)
            c += '}<br><br>'
        c += '</body>'
        return HttpResponse(c)
    get_confirmations.short_description = 'Generovať potvrdenia o účasti'


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('meno', 'pohlavie', 'tim')
    list_filter = ('pohlavie', 'bageta', 'tim')
    list_per_page = 100
    search_fields = ('meno', 'tim')
    ordering = ('-pk',)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('meno', 'mail', 'tim')
    list_per_page = 100
    search_fields = ('meno', 'tim')
    ordering = ('-pk',)

    def tim(self, teacher):
        try:
            return Team.objects.filter(ucitel=teacher).order_by('-pk')[0]
        except(IndexError):
            return None

    # Renames column head
    tim.short_description = 'Trénuje tím'


# admin.site.register(Model, ModelAdmin)

admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(FinalMember, PlayerAdmin)
admin.site.register(Teacher, TeacherAdmin)

admin.site.site_header = 'Stredoškolská Liga Ultimate Frisbee'
admin.site.site_title = 'SLU'
admin.site.index_title = 'Domov'
admin.site.site_url = '/prihlasovanie/'
