from game_night_slack.auth import GameNightAuth
from os import environ
from flask import request
from requests import get
from urllib.parse import urljoin
from fuzzywuzzy.process import extractOne

_game_mapper = lambda game: '*' + game['name'] + '*'

_auth = GameNightAuth(environ['GAME_NIGHT_API_KEY'])

def newest():
    arguments = request.form['text'].split()
    params = {}
    if _parse_arguments(arguments, params) is None:
        return 'Usage: /gn-newest [-p|--players]', True
    games = get(urljoin(environ['GAME_NIGHT_URL'], 'newest'), auth = _auth, params = params).json()
    if len(games) == 0:
        return 'None of the newest games support {} player(s).'.format(params['players']), False
    elif len(games) == 1:
        try:
            return 'One of the newest games that supports {} player(s) is *{}*.'.format(params['players'], games[0]['name']), False
        except:
            return 'The newest game is *{}*.'.format(games[0]['name']), False
    extra = ' that support {} player(s)'.format(params['players']) if 'players' in params else ''
    return 'The {} newest games{} are {}.'.format(len(games), extra, ', '.join(map(_game_mapper, games))), False

def owner():
    name = request.form['text']
    if name:
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = {'name': name}).json()
        if games:
            name = extractOne(name, map(lambda game: game['name'], games))[0]
            game = next(filter(lambda game : game['name'] == name, games))
            return '*{}* owns *{}*.'.format(game.get('owner', 'CSH'), game['name']), False
        return 'No one owns "{}".'.format(name), False
    return 'Usage: /gn-owner name', True

def _parse_arguments(arguments, params):
    if arguments and arguments[0] in ['-p', '--players']:
        try:
            params['players'] = int(arguments[1])
            arguments = arguments[2:]
        except:
            return None
    return arguments

def search():
    arguments = request.form['text'].split()
    if arguments:
        params = {}
        arguments = _parse_arguments(arguments, params)
        if arguments is None:
            return 'Usage: /gn-search [-p|--players] name', True
        params['name'] = ' '.join(arguments)
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = params).json()
        if len(games) == 0:
            extra = ' and support {} player(s)'.format(params['players']) if 'players' in params else ''
            return 'We don\'t have any games that match "{}"{}.'.format(params['name'], extra), False
        elif len(games) == 1:
            extra = ' and supports {} player(s)'.format(params['players']) if 'players' in params else ''
            return 'We have 1 game that matches "{}"{} - *{}*.'.format(params['name'], extra, games[0]['name']), False
        extra = ' and support {} player(s)'.format(params['players']) if 'players' in params else ''
        return 'We have {} games that match "{}"{} - {}.'.format(len(games), params['name'], extra, ', '.join(map(_game_mapper, games))), False
    return 'Usage: /gn-search [-p|--players] name', True