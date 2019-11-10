from django.contrib import admin


class OrderedAdminSite(admin.AdminSite):

    def get_app_list(self, request):
        app_ordering = {
            'používateľ': 0,
            'autentifikácia a autorizácia': 1,
            'obsah': 2,
            'turnajový správca': 3,
            'registrácia': 4
        }

        model_ordering = [{
            'používatelia': 1
        }, {
            'oprávnenia':1,
            'skupiny':2,
        }, {
            'novinky': 1,
            'sekcie': 2,
            'profily organizátorov': 3,
            'správy': 4,
        }, {
            'sezóny': 2,
            'turnaje': 3,
            'tímy': 1,
            'zápasy': 5,
            'body': 6,
            'výsledky': 4,
            'fotky': 7,
        }, {
            'školy': 1,
            'hráči': 2,
            'učitelia': 3,
        }]

        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: app_ordering[x['name'].lower()])

        for i in range(len(app_list)):
            app_list[i]['models'].sort(
                key=lambda x: model_ordering[i][x['name'].lower()]
            )

        return app_list
