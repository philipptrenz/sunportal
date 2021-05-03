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

CONFIG = Config()
DB = Database(config=CONFIG)
MAIL = Mail(CONFIG, DB)
APP = Flask(__name__)

SCHEMA = {
    'type': 'object',
    'properties': {
        'date': {
            'type': 'string',
            "pattern": r'^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'
        },
        'requested_data': {
            'type': 'object',
            "properties" : {
                "day" : {"type" : "boolean"},
                "month" : {"type" : "boolean"},
                "year" : {"type" : "boolean"},
                "tot" : {"type" : "boolean"}
            }
        }
    },
    'required': ['date', 'requested_data']
}


@APP.route('/')
def home():
    """Set html file"""
    return render_template('index.html')


@APP.route('/update', methods=['POST'])
@expects_json(SCHEMA)
def update():
    """Do the request"""
    val = jsonify()
    if request.headers['Content-Type'] == 'application/json':
        content = request.json
        if 'date' not in content:
            flask.abort(400)
        if 'requested_data' not in content:
            flask.abort(400)
        date = content['date']
        requested_data = content['requested_data']
        val = jsonify(DB.get(date, requested_data))
    return val

if __name__ == '__main__':
    if MAIL.is_enabled:
        MAIL.start()
    APP.run(host='0.0.0.0', port=80)
