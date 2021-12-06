#!/usr/bin/python3
"""
sunportal is a web based visualisation tool to display data of SMA solar inverters.
It is based on the database of SBFspot and shows charts daily and monthly power
production. It runs on a Raspberry Pi and can handle multiple inverters in one Speedwire
or Bluetooth(R) network.
"""

import flask
from flask import Flask, render_template, request, jsonify
from flask_expects_json import expects_json

from util.config import Config
from util.database import Database
from util.mail import Mail

config = Config()
db = Database(config=config)
mail = Mail(config, db)
app = Flask(__name__)

schema = {
    'type': 'object',
    'properties': {
        'date': {
            'type': 'string',
            "pattern": r'^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'
        }
    },
    'required': ['date']
}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/update', methods=['POST'])
@expects_json(schema)
def update():
    if request.headers['Content-Type'] == 'application/json':
        content = request.json
        if 'date' not in content: flask.abort(400)
        date = content['date']
        return jsonify(db.get(date))
    flask.abort(400)

if __name__ == '__main__':
    if mail.is_enabled: mail.start()
    app.run(host='0.0.0.0', port=8080)
