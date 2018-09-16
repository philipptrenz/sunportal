#!/usr/bin/python3
"""
"""
import time, flask
from flask import Flask, render_template, request, json, jsonify
import sqlite3
from datetime import datetime


app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
	if request.headers['Content-Type'] == 'application/json':
		content = request.json
		print(content)
		if 'date' not in content: flask.abort(400)
		date = content['date']

		return get_db_data(date)

	else:
		flask.abort(400)


def get_db_data(date):
	db = sqlite3.connect('SBFspot.db')

	c = db.cursor()
	c.row_factory = sqlite3.Row

	c.execute('''
		SELECT Serial, TimeStamp, EToday, ETotal, Status, OperatingTime
		FROM SpotData 
		WHERE TimeStamp == (SELECT MAX(TimeStamp) FROM SpotData);
	''')

	result = [dict(row) for row in c.fetchall()]
	print(result)

	return '{}'

def get_epoch(date):
	epoch = datetime(1970, 1, 1)
	epoch_time = (datetime.strptime(date, "%Y-%m-%d") - epoch).total_seconds()
	return int(epoch_time)

###############################################

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)