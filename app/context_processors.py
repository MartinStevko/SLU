from datetime import datetime
from tournament.models import Season, Tournament


def variables_processor(request):
    r = {}

    season = Season.objects.all().order_by('-pk')
    if season:
        season = season[0]

        if season.season == 'indoor':
            r.update({'indoor': True})
        else:
            r.update({'outdoor': True})

    else:
        r.update({'outdoor': True})

    user = request.user
    if user.is_authenticated:
        t = user.tournament_set.filter(date__gte=datetime.now())
        print(t)
        r.update({'my_tournaments': t})

    return r
