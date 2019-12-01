from django.test import TestCase

import datetime


class CustomSeason:
    pk = 1
    orgs = ['C.Org 1', 'C.Org 2']
    school_year = '2018/2019'
    season = 'outdoor'
    game_format = 'loose_mix'


class CustomTournament:
    pk = 1
    season = CustomSeason()
    state = 'registration'
    orgs = ['L.Org 1', 'L.Org 2']
    delegate = 'SAF delegat'
    director = 'Ted'
    institute = 'SLU-cka'
    date = datetime.date.today()
    place = 'SOS Ostrovskeho'
    in_city = 'Kosiciach'
    image = 'Obr. 1'
    prop_image = 'Obr. 2'
    cap = True
    game_duration = '24:00'
    region = 'F'
    player_stats = True
    number_qualified = 3
    max_teams = 16
    signup_deadline = datetime.datetime(2019, 12, 31, 23, 59, 59)
    arrival_time = datetime.time(8, 0)
    meeting_time = datetime.time(9, 0)
    game_time = datetime.time(10, 0)
    end_time = datetime.time(16, 0)


class CustomSchool:
    pk = 1
    name = 'Gymnazium'
    web = 'https://slu.szf.sk/'
    street = 'Alejova 1'
    postcode = '044 61'
    city = 'Kosice'
    region = 'E'
    have_disc = True


class CustomTeacher:
    pk = 1
    school = CustomSchool()
    first_name = 'John'
    last_name = 'Doe'
    email = 'john.doe@slu.sk'
    phone_number = '+421 123 456 789'


class CustomTeam:
    pk = 1
    tournament = CustomTournament()
    confirmed = True
    status = 'invited'
    school = CustomSchool()
    teacher = CustomTeacher()
    players = ['Plater 1', 'Player 2']
    name = 'SLU herny tim'
    extra_email = ''
    identifier = 'vf1brf4vfsdb5v4'
    accept_gdpr = True
