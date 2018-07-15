from game_night_slack.commands import newest, owner, search
from flask import abort, Flask, jsonify, request
from os import environ

commands = {
    '/gn-newest': newest,
    '/gn-owner': owner,
    '/gn-search': search
}

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def main():
    if request.form.get('token') == environ['SLACK_VERIFICATION_TOKEN']:
        command = commands.get(request.form.get('command'))
        if command:
            text, error = command()
            return jsonify({'response_type': 'ephemeral' if error else 'in_channel', 'text': text})
    abort(403)