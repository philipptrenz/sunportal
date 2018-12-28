#!/usr/bin/python3
"""
"""
import json
import sqlite3
import pytz
from datetime import datetime
from util.database import Database
from util.config import Config

def get_datetime_from_timestamp(tz):
    return datetime.fromtimestamp(tz, tz=db.get_local_timezone())

def get_yield_as_array(serial_id, datestring):
    res = db.get_requested_day_for_inverter(serial_id, datestring)

#    print(datetime.fromtimestamp(res['interval']['from'], tz=db.get_local_timezone()))
#    print(datetime.fromtimestamp(res['interval']['to'], tz=db.get_local_timezone()))
#    print(datetime.fromtimestamp(res['interval']['to'], tz=db.get_local_timezone()).tzinfo)

    data = res['data']

    arr = []

    tz = res['interval']['from']
    assert(tz % 300 == 0)
    while tz < data[0]['time']:
        arr.append(0)
        tz += 5*60 # every 5 minutes

    prev = tz - 5*60
    for obj in data:
        try:
            assert(prev+5*60==obj['time'])
        except AssertionError as e:
            #print(e, 'i:', i,'prev:', prev, 'prev+5*60', (prev+5*60), 'obj[time]', obj['time'])
            #raise AssertionError()
            p_prev = prev+5*60
            while p_prev < obj['time']:
                arr.append(0)
                p_prev += 5*60

        arr.append(obj['power'])
        prev = obj['time']

    prev = data[-1]['time']+5*60
    while prev < res['interval']['to']:
        arr.append(0)
        prev+=5*60

    assert(len(arr)==int(24*60/5))

    return arr

def collect_and_save_data(serial_id, datestrings):

    file = []

    i = 0
    for s in datestrings:
        tmp = get_yield_as_array(serial_id, s)
        file.append( { 'name': 'case_'+str(i), 'data': tmp } )
        i+=1

    with open('dummy_yield_data.json', 'w') as fp:
        json.dump(file, fp, indent=4, sort_keys=True)


def get_dummy_yield_data_for_day(year, month, day, dummy_yield_data_id, serial_id, sqlite_db_path=':memory:', timezone_offset_in_hours=0):

    conn = sqlite3.connect(sqlite_db_path)
    c = conn.cursor()

    day_data = {}

    with open('dummy_yield_data.json', 'r') as fp:
        data = json.load(fp)

        dummy_data = {}
        try:
            dummy_data = data[dummy_yield_data_id]
        except IndexError:
            raise IndexError('Requested dummy yield data id is not in dummy_yield_data.json')

        datetime_obj = datetime(year, month, day, 00, 00, 00)
        timestamp = int(datetime_obj.timestamp())
        total_day_ts = int(datetime(year, month, day, 23).timestamp())

        if timezone_offset_in_hours is not 0:
            timestamp += timezone_offset_in_hours * 60 * 60
            total_day_ts += timezone_offset_in_hours * 60 * 60

        ts = timestamp
        total_day_yield = 0
        day_data['daydata'] = []
        for power in dummy_data['data']:
            if power > 0: day_data['daydata'].append({'ts':ts, 'power':power})
            total_day_yield += power
            ts += 60*60

        day_data['monthdata'] = {'ts':total_day_ts, 'yield':total_day_yield}

        return day_data



if __name__ == '__main__':

    def generate_dummy_yield_data_json():

        cfg = Config('./config.yml')
        db = Database(cfg)

        datestrings = [
            '2018-10-01',
            '2018-10-02',
            '2018-10-03',
            '2018-10-04',
            '2018-10-05',
        ]

        serial_id = '2000079685'

        collect_and_save_data(serial_id, datestrings)

    # generate_dummy_yield_data_json()
    # show()

    data = get_dummy_yield_data_for_day(2018, 11, 29, dummy_yield_data_id=2, serial_id='1000000001')

    print(data)




