from datetime import datetime
from tournament.models import Season


def variables_processor(request):
    r = {}

    season = Season.objects.all().order_by('-pk')[0]
    if season.season == 'indoor':
        r.update({'indoor': True})
    else:
        r.update({'outdoor': True})

    return r
