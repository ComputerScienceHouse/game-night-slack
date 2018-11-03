from urllib.parse import urljoin
from os import environ
from game_night_slack.auth import GameNightAuth
from flask import request
from requests import get
from fuzzywuzzy.process import extractOne

_count_url = urljoin(environ['GAME_NIGHT_URL'], 'count')
_games = lambda games: ', '.join((f'*{game["name"]}*' for game in games))
_newest_url = urljoin(environ['GAME_NIGHT_URL'], 'newest')
_parameters = lambda params: f'({", ".join((key + "=" + value for key, value in params.items()))})'
_unreachable = 'Game Night is unreachable at the moment. Please try again later.', True

_auth = GameNightAuth(environ['GAME_NIGHT_API_KEY'])

def info():
    name = request.form.get('text')
    if not name:
        return _info_usage
    try:
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = {'name': name}).json()
    except:
        return _unreachable
    if not games:
        return f'"{name}" doesn\'t exist.', False
    name = extractOne(name, (game['name'] for game in games))[0]
    game = next(game for game in games if game['name'] == name)
    text = f'*<{game["link"]}|{game["name"]}>*\n\n'
    try:
        text += f'Expansion: *{game["expansion"]}*\n'
    except:
        pass
    return text + f'''Owner: *{game["owner"]}*
Players: *{game["min_players"]}* - *{game["max_players"]}*
Submitter: *{game["submitter"]}*
''', False

def newest():
    arguments = request.form.get('text', '').split()
    params = {}
    try:
        _parse_parameters(arguments, params)
    except:
        return _newest_usage
    try:
        games = get(_newest_url, auth = _auth, params = params).json()
    except:
        return _unreachable
    if len(games) == 0:
        return f'None of the newest games match the parameters {_parameters(params)}.', False
    elif len(games) == 1:
        return f'The newest game that matches the parameters {_parameters(params)} is *{games[0]["name"]}*.', False
    return f'The {len(games)} newest games that match the parameters {_parameters(params)} are {_games(games)}.', False

def _parse_parameters(arguments, params):
    while arguments and arguments[0] in ['-o', '--owner', '-p', '--players', '-s', '--submitter']:
        if '-o' in arguments[0]:
            params['owner'] = arguments[1]
        elif '-p' in arguments[0]:
            params['players'] = arguments[1]
        else:
            params['submitter'] = arguments[1]
        arguments = arguments[2:]
    return arguments

def search():
    params = {}
    try:
        arguments = _parse_parameters(request.form.get('text', '').split(), params)
    except:
        return _search_usage
    if arguments:
        params['name'] = ' '.join(arguments)
    elif not params:
        return 'This query would return all games. Use some filters to narrow down the results.', True
    try:
        count = get(_count_url, auth = _auth).json()
        games = get(environ['GAME_NIGHT_URL'], auth = _auth, params = params).json()
    except:
        return _unreachable
    if len(games) == 0:
        return f'We don\'t have any games that match the parameters {_parameters(params)}.', False
    elif len(games) == 1:
        return f'We have 1 game that matches the parameters {_parameters(params)} - *{games[0]["name"]}*.', False
    if count == len(games):
        return 'This query would return all games. Use different filters to narrow down the results.', True
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
`-p`, `--players`\tNarrow down the results by the supported number of players.
`-s`, `--submitter`\tNarrow down the results by the specified game submitter.'''
    return usage, True

_info_usage = _usage('info', False, [('name', False)])
_newest_usage = _usage('newest', True)
_search_usage = _usage('search', True, [('name', True)])