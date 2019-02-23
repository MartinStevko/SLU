from datetime import datetime
from tournament.models import Season


def variables_processor(request):
    r = {}

    season = Season.objects.all().order_by('-pk')
    if season:
        season = season[0]
    else:
        r.update({'outdoor': True})

    if season.season == 'indoor':
        r.update({'indoor': True})
    else:
        r.update({'outdoor': True})

    return r
