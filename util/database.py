#!/usr/bin/python3
"""
"""
import sqlite3, json
from datetime import datetime, date, time, timedelta

class Database():

    def __init__(self, db_file='./SBFspot.db', co2_mult=0.7):
        self.co2_mult = co2_mult
        self.db = sqlite3.connect(db_file, check_same_thread=False)
        self.c = self.db.cursor()

    def get(self, date):
        data = dict()
        data['today'] = self.get_today()
        data['requested'] = self.get_requested(date)
        return data

    def get_today(self):

        query = '''
            SELECT Serial, TimeStamp, EToday, ETotal, Status, OperatingTime
            FROM SpotData 
            WHERE TimeStamp == (SELECT MAX(TimeStamp) FROM SpotData);
            '''

        data = dict()
        total_day=0
        total=0
        co2=0

        data['inverters'] = dict()
        for row in self.c.execute(query):
            serial = str(row[0])
            data['inverters'][serial] = dict()
            data['inverters'][serial]['lastUpdated'] = row[1]
            data['inverters'][serial]['dayTotal'] = row[2]
            data['inverters'][serial]['total'] = row[3]
            data['inverters'][serial]['status'] = row[4]
            data['inverters'][serial]['operatingTime'] = row[5]

            inv_co2 = round(row[3] / 1000 * self.co2_mult)
            data['inverters'][serial]['co2'] = inv_co2

            total_day += row[2]
            total += row[3]
            co2 += inv_co2

        data['dayTotal'] = total_day
        data['total'] = total
        data['co2'] = co2

        return data

    def get_requested(self, date):

        data = dict()
        data['date'] = date

        data['all'] = dict()
        data['all']['day'] = self.get_requested_day(date)
        data['all']['month'] = self.get_requested_month(date)

        data['inverters'] = list()

        return data

    def get_requested_day(self, date):

        data = dict()

        day_start, day_end = self.get_epoch_day(date)
        data['interval'] = {'from': day_start, 'to': day_end}
        day_total = 0

        query = '''
            SELECT TimeStamp, SUM(Power) AS Power 
			FROM DayData 
			WHERE TimeStamp BETWEEN %s AND %s 
			GROUP BY TimeStamp;
            '''

        data['data'] = list()
        for row in self.c.execute(query % (day_start, day_end)):
            data['data'].append({ 'time': row[0], 'power': row[1] })
            day_total += row[1]


#        query = '''
#            SELECT SUM(EToday) as EToday
#			FROM SpotData
#			WHERE TimeStamp == (SELECT MAX(TimeStamp) FROM SpotData WHERE TimeStamp BETWEEN %s AND %s );
#            '''
#
#        self.c.execute(query % (day_start, day_end))
#        data['total'] = self.c.fetchone()[0]
        data['total'] = day_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max 
			FROM ( SELECT TimeStamp FROM DayData GROUP BY TimeStamp );
            '''

        self.c.execute(query)
        first_data, last_data = self.c.fetchone()

        data['hasPrevious'] = (first_data < day_start)
        data['hasNext'] = (last_data > day_end)

        #print(json.dumps(data, indent=4))
        return data

    def get_requested_month(self, date):
        data = dict()

        month_start, month_end = self.get_epoch_month(date)
        data['interval'] = {'from': month_start, 'to': month_end}
        month_total = 0

        query = '''
            SELECT TimeStamp, SUM(DayYield) AS Power 
            FROM MonthData 
            WHERE TimeStamp BETWEEN %s AND %s
            GROUP BY TimeStamp
            '''

        data['data'] = list()
        for row in self.c.execute(query % (month_start, month_end)):
            data['data'].append({'time': row[0], 'power': row[1]})
            month_total += row[1]

        data['total'] = month_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max 
            FROM ( SELECT TimeStamp FROM MonthData GROUP BY TimeStamp );
            '''

        self.c.execute(query)
        first_data, last_data = self.c.fetchone()

        data['hasPrevious'] = (first_data < month_start)
        data['hasNext'] = (last_data > month_end)

        return data

    def get_epoch(self, date):
        epoch = datetime(1970, 1, 1)
        epoch_time = (datetime.strptime(date, "%Y-%m-%d") - epoch).total_seconds()
        return int(epoch_time)

    def get_epoch_day(self, date):
        epoch = datetime(1970, 1, 1)
        epoch_start = (datetime.strptime(date + " 00:00:00", "%Y-%m-%d %H:%M:%S") - epoch).total_seconds()
        epoch_end = (datetime.strptime(date + " 23:59:59", "%Y-%m-%d %H:%M:%S") - epoch).total_seconds()
        return int(epoch_start), int(epoch_end)

    def get_epoch_month(self, date):
        epoch = datetime(1970, 1, 1)
        epoch_start = (datetime.strptime(date[:7] + "-01 00:00:00", "%Y-%m-%d %H:%M:%S") - epoch).total_seconds()
        month_end = str(self.get_last_day_of_month(date))[:10]
        epoch_end = (datetime.strptime(month_end + " 23:59:59", "%Y-%m-%d %H:%M:%S") - epoch).total_seconds()
        return int(epoch_start), int(epoch_end)

    def get_last_day_of_month(self, date):
        day = datetime.strptime(date, "%Y-%m-%d")
        next_month = day.replace(day=28) + timedelta(days=4)  # this will never fail
        return next_month - timedelta(days=next_month.day)

    def close(self):
        self.db.close()

if __name__ == '__main__':
    db = Database('../SBFspot.db')

    date = '2018-09-16'

    data =  db.get(date)
    print(json.dumps(data , indent=4))
