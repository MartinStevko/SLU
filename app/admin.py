from django.contrib import admin


class OrderedAdminSite(admin.AdminSite):

    def get_app_list(self, request):
        app_ordering = {
            'autentifikácia a autorizácia': 1,
            'obsah': 3,
            'turnajový správca': 4,
            'registrácia': 5
        }

        model_ordering = [{
            'používatelia': 1,
            'skupiny': 2,
        }, {
            'novinky': 1,
            'sekcie': 2,
            'profily organizátorov': 3,
            'správy': 4,
        }, {
            'sezóny': 1,
            'turnaje': 2,
            'tímy': 3,
            'zápasy': 4,
            'body': 5,
            'výsledky': 6,
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
