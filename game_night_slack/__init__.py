from flask import abort, Flask, jsonify, request
from os import environ
from game_night_slack.commands import search

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def main():
    if request.form.get('token') == environ['SLACK_VERIFICATION_TOKEN']:
        if request.form.get('command') == '/gn-search':
            return jsonify({'response_type': 'in_channel', 'text': search()})
    abort(403)
