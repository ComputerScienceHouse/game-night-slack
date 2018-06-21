from game_night_slack.auth import GameNightAuth
from os import environ
from flask import request
from requests import get
from fuzzywuzzy.process import extractOne

_auth = GameNightAuth(environ['GAME_NIGHT_API_KEY'])

def owner():
    name = request.form['text']
    if name:
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = {'name': name}).json()
        if games:
            name = extractOne(name, map(lambda game: game['name'], games))[0]
            game = next(filter(lambda game : game['name'] == name, games))
            return '*{}* owns *{}*.'.format(game.get('owner', 'CSH'), game['name'])
        return 'No one owns "{}".'.format(name)
    return 'Usage: /gn-owner name'


def search():
    arguments = request.form['text'].split()
    if arguments:
        params = {}
        if arguments[0] in ['-p', '--players']:
            try:
                params['players'] = int(arguments[1])
                arguments = arguments[2:]
            except:
                return 'Usage: /gn-search [-p|--players] name'
        params['name'] = ' '.join(arguments)
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = params).json()
        if len(games) == 0:
            extra = ' and support {} player(s)'.format(params['players']) if 'players' in params else ''
            return 'We don\'t have any games that match "{}"{}.'.format(params['name'], extra)
        elif len(games) == 1:
            extra = ' and supports {} player(s)'.format(params['players']) if 'players' in params else ''
            return 'We have 1 game that matches "{}"{} - *{}*.'.format(params['name'], extra, games[0]['name'])
        extra = ' and support {} player(s)'.format(params['players']) if 'players' in params else ''
        return 'We have {} games that match "{}"{} - {}.'.format(len(games), params['name'], extra, ', '.join(map(lambda game: '*' + game['name'] + '*', games)))
    return 'Usage: /gn-search [-p|--players] name'