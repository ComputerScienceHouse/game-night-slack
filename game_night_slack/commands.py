from game_night_slack.auth import GameNightAuth
from os import environ
from flask import request
from requests import get
from urllib.parse import urljoin
from fuzzywuzzy.process import extractOne

_games = lambda games: ', '.join((f'*{game["name"]}*' for game in games))
_parameters = lambda params: f'({", ".join((key + "=" + value for key, value in params.items()))})'
_unreachable = 'Game Night is unreachable at the moment. Please try again later.', True

_auth = GameNightAuth(environ['GAME_NIGHT_API_KEY'])

def newest():
    arguments = request.form.get('text', '').split()
    params = {}
    if _parse_parameters(arguments, params) is None:
        return _usage('newest', True)
    try:
        games = get(urljoin(environ['GAME_NIGHT_URL'], 'newest'), auth = _auth, params = params).json()
    except:
        return _unreachable
    if len(games) == 0:
        return f'None of the newest games match the parameters {_parameters(params)}.', False
    elif len(games) == 1:
        return f'The newest game that matches the parameters {_parameters(params)} is *{games[0]["name"]}*.', False
    return f'The {len(games)} newest games that match the parameters {_parameters(params)} are {_games(games)}.', False

def owner():
    name = request.form.get('text')
    if name:
        try:
            games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = {'name': name}).json()
        except:
            return _unreachable
        if games:
            name = extractOne(name, (game['name'] for game in games))[0]
            game = next((game for game in games if game['name'] == name))
            return f'*{game.get("owner", "CSH")}* owns *{game["name"]}*.', False
        return f'No one owns "{name}".', False
    return _usage('owner', False, [('name', False)])

def _parse_parameters(arguments, params):
    while arguments and arguments[0] in ['-o', '--owner', '-p', '--players']:
        try:
            if '-o' in arguments[0]:
                params['owner'] = arguments[1]
            else:
                params['players'] = arguments[1]
            arguments = arguments[2:]
        except:
            return None
    return arguments

def search():
    params = {}
    arguments = _parse_parameters(request.form.get('text', '').split(), params)
    if arguments is None:
        return _usage('search', True, [('name', True)])
    if arguments:
        params['name'] = ' '.join(arguments)
    elif not params:
        return 'This query would return all games. Use some filters to narrow down the results.', True
    try:
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = params).json()
    except:
        return _unreachable
    if len(games) == 0:
        return f'We don\'t have any games that match the parameters {_parameters(params)}.', False
    elif len(games) == 1:
        return f'We have 1 game that matches the parameters {_parameters(params)} - *{games[0]["name"]}*.', False
    return f'We have {len(games)} games that match the parameters {_parameters(params)} - {_games(games)}.', False

def _usage(command, params = False, arguments = []):
    usage = f'Usage: `/gn-{command}`'
    if params:
        usage += ' [`OPTION`...]'
    for argument, optional in arguments:
        usage += f' [`{argument}`]' if optional else f' `{argument}`'
    if params:
        usage += '''\nWhere `OPTION` is one of:

`-o`, `--owner`\t\tNarrow down the results by the specified game owner.
`-p`, `--players`\tNarrow down the results by the supported number of players.'''
    return usage, True