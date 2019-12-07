from django.contrib import admin
from django.apps import apps
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

APP_ORDERING = {
    'user': 1,
    'auth': 2,
    'content': 3,
    'checklist': 4,
    'tournament': 5,
    'registration': 6,
    'emails': 7,
}

MODEL_ORDERING = {
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
    'checklist': {
        'document': 1,
        'task': 2,
        'checklist': 3,
    },
    'tournament': {
        'team': 1,
        'season': 2,
        'tournament': 3,
        'result': 4,
        'match': 5,
        'spiritscore': 6,
        'point': 7,
        'photo': 8,
        'abstractgallery': 9,
    }, 
    'registration': {
        'school': 1,
        'teacher': 2,
        'player': 3,
    }, 
    'emails': {
        'template': 1,
        'generic': 2,
    }
}


class OrderedAdminSite(admin.AdminSite):

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: APP_ORDERING[x['app_label'].lower()])

        for app in app_list:
            key = app['app_label']
            app['models'].sort(
                key=lambda x: MODEL_ORDERING[key][x['object_name'].lower()]
            )

            if key == 'tournament':
                for model in app['models']:
                    if model['object_name'].lower() == 'abstractgallery':
                        app['models'] = app['models'][:-1]

        return app_list

    def app_index(self, request, app_label, extra_context=None):
        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')

        app_dict['models'].sort(
            key=lambda x: MODEL_ORDERING[app_label][x['object_name'].lower()]
        )

        if app_label == 'tournament':
            for model in app_dict['models']:
                if model['object_name'].lower() == 'abstractgallery':
                    app_dict['models'] = app_dict['models'][:-1]

        app_name = apps.get_app_config(app_label).verbose_name
        context = {
            **self.each_context(request),
            'title': _('%(app)s administration') % {'app': app_name},
            'app_list': [app_dict],
            'app_label': app_label,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context)
