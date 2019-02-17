from game_night_slack.commands import info, newest, search
from flask import abort, Flask, jsonify, request
from os import environ

_commands = {
    '/gn-info': info,
    '/gn-newest': newest,
    '/gn-search': search
}

app = Flask(__name__)

@app.route('/' + environ.get('ENDPOINT', ''), methods = ['POST'])
def main():
    if request.form.get('token') == environ['SLACK_VERIFICATION_TOKEN']:
        try:
            text, error = _commands[request.form['command']]()
            return jsonify({'response_type': 'ephemeral' if error else 'in_channel', 'text': text})
        except:
            pass
    abort(403)