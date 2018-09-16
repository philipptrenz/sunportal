#!/usr/bin/python3
"""
"""
import flask, json
from flask import Flask, render_template, request, json, jsonify

from util.config import Config
from util.database import Database


config = Config()
db = Database(config=config)
app = Flask(__name__)


@app.route('/')
def home():
	return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
	if request.headers['Content-Type'] == 'application/json':
		content = request.json
		if 'date' not in content: flask.abort(400)
		date = content['date']
		return jsonify(db.get(date))

	else:
		flask.abort(400)

###############################################

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)