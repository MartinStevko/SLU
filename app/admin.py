from django.contrib import admin


class OrderedAdminSite(admin.AdminSite):

    def get_app_list(self, request):
        app_ordering = {
            'user': 0,
            'auth': 1,
            'content': 2,
            'tournament': 3,
            'registration': 4,
            'emails': 5,
        }

        model_ordering = {
            'user': {
                'user': 1
            }, 
            'auth': {
                'permission':1,
                'group':2,
            }, 
            'content': {
                'news': 1,
                'section': 2,
                'organizerprofile': 3,
                'message': 4,
            }, 
            'tournament': {
                'team': 1,
                'season': 2,
                'tournament': 3,
                'result': 4,
                'match': 5,
                'point': 6,
                'photo': 7,
            }, 
            'registration': {
                'school': 1,
                'teacher': 2,
                'player': 3,
            }, 
            'emails': {
                'template': 1,
            }
        }

        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: app_ordering[x['app_label'].lower()])

        for i in range(len(app_list)):
            key = app_list[i]['app_label']
            app_list[i]['models'].sort(
                key=lambda x: model_ordering[key][x['object_name'].lower()]
            )

        return app_list
