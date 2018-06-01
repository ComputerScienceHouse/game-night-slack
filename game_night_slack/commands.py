from game_night_slack.auth import GameNightAuth
from os import environ
from flask import request
from requests import get

_auth = GameNightAuth(environ['GAME_NIGHT_API_KEY'])

def owner():
    name = request.form['text']
    if name:
        game = get(environ['GAME_NIGHT_URL'], auth = _auth, params = {'name': '^' + name + '$'}).json()
        if game:
            game = game[0]
            return '*{}* owns *{}*.'.format(game.get('owner', 'CSH'), game['name'])
        return 'No one owns "{}".'.format(name)
    return 'Usage: /gn-owner name'


def search():
    name = request.form['text']
    if name:
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = {'name': name}).json()
        if len(games) == 0:
            return 'We don\'t have any games that match "{}".'.format(name)
        elif len(games) == 1:
            return 'We have 1 game that matches "{}" - *{}*.'.format(name, games[0]['name'])
        return 'We have {} games that match "{}" - {}.'.format(len(games), name, ', '.join(map(lambda game: '*' + game['name'] + '*', games)))
    return 'Usage: /gn-search name'