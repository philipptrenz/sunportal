#!/usr/bin/python3
"""
"""
import pytz
import sqlite3
from datetime import datetime, timedelta


class Database():

    def __init__(self, config):
        self.config = config
        self.co2_mult = self.config.get_co2_avoidance_factor()
        self.db = sqlite3.connect(self.config.get_database_path(), check_same_thread=False)
        self.c = self.db.cursor()

        self.local_timezone = self.get_local_timezone()

    def get(self, date, requested_data):
        tot_start, tot_end = self.get_epoch_tot()
        int_date = int(datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]), 00, 00, 00, tzinfo=pytz.utc).timestamp())
        if int_date < tot_start:
            date = datetime.utcfromtimestamp(tot_start).strftime('%Y-%m-%d')
        if int_date > tot_end:
            date = datetime.utcfromtimestamp(tot_end).strftime('%Y-%m-%d')
        data = dict()
        data['today'] = self.get_today()
        data['requested'] = self.get_requested(date, requested_data)
        return data

    def get_today(self):

        data = dict()
        total_day = 0
        total = 0
        co2 = 0

        data['inverters'] = dict()
        inverters = self.get_inverters()
        for inv in inverters:

            inv_co2 = 0
            if inv['etotal'] is not None:
                inv_co2 = round(inv['etotal'] / 1000 * self.co2_mult)

            data['inverters'][inv['serial']] = {
                'serial': inv['serial'],
                'name': inv['name'],
                'lastUpdated': inv['ts'],
                'dayTotal': inv['etoday'],
                'total': inv['etotal'],
                'status': inv['status'],
                'co2': inv_co2
            }

            if inv['etoday'] is not None: total_day += inv['etoday']
            if inv['etotal'] is not None: total += inv['etotal']
            co2 += inv_co2

        data['dayTotal'] = total_day
        data['total'] = total
        data['co2'] = co2

        return data

    def get_requested(self, date, requested_data):
        data = dict()
        data['date'] = date

        data['all'] = dict()
        if requested_data['day'] is True:
            data['all']['day'] = self.get_requested_day(date)
        if requested_data['month'] is True:
            data['all']['month'] = self.get_requested_month(date)
        if requested_data['year'] is True:
            data['all']['year'] = self.get_requested_year(date)
        if requested_data['tot'] is True:
            data['all']['tot'] = self.get_requested_tot()

        data['inverters'] = dict()

        inverters = self.get_inverters()
        for inv in inverters:
            data['inverters'][inv['serial']] = { 'day': [], 'month': [], 'year': [], 'tot': [] }

            if requested_data['day'] is True:
                data['inverters'][inv['serial']]['day'] = self.get_requested_day_for_inverter(inv['serial'], date)
            if requested_data['month'] is True:
                data['inverters'][inv['serial']]['month'] = self.get_requested_month_for_inverter(inv['serial'], date)
            if requested_data['year'] is True:
                data['inverters'][inv['serial']]['year'] = self.get_requested_year_for_inverter(inv['serial'], date)
            if requested_data['tot'] is True:
                data['inverters'][inv['serial']]['tot'] = self.get_requested_tot_for_inverter(inv['serial'])

        return data

    def get_requested_day(self, date):

        data = dict()

        day_start, day_end = self.get_epoch_day(date)
        data['interval'] = {'from': self.convert_local_ts_to_utc(day_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(day_end, self.local_timezone)}

        query = '''
            SELECT TimeStamp, SUM(Power) AS Power
            FROM DayData
            WHERE TimeStamp BETWEEN ? AND ?
            GROUP BY TimeStamp;
        '''

        data['data'] = list()
        for row in self.c.execute(query, (day_start, day_end)):
            data['data'].append({ 'time': row[0], 'power': row[1] })


        if self.get_datetime(date).date() == datetime.today().date():
            query = '''
                SELECT SUM(EToday) as EToday
                FROM Inverters;
                '''
            self.c.execute(query)
        else:
            query = '''
                SELECT SUM(DayYield) AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ?
                GROUP BY TimeStamp;
                '''
            self.c.execute(query, (day_start, day_end))

        row = self.c.fetchone()
        if row and row[0]: data['total'] = row[0]
        else: data['total'] = self.get_today()['dayTotal']


        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM DayData GROUP BY TimeStamp );
            '''

        self.c.execute(query)
        first_data, last_data = self.c.fetchone()

        if (first_data):  data['hasPrevious'] = (first_data < day_start)
        else: data['hasPrevious'] = False

        if (last_data): data['hasNext'] = (last_data > day_end)
        else: data['hasNext'] = False

        #print(json.dumps(data, indent=4))
        return data

    def get_requested_day_for_inverter(self, inverter_serial, date):
        data = dict()

        day_start, day_end = self.get_epoch_day(date)
        data['interval'] = {'from': self.convert_local_ts_to_utc(day_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(day_end, self.local_timezone)}

        query = '''
            SELECT TimeStamp, Power
            FROM DayData
            WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
            '''

        data['data'] = list()
        for row in self.c.execute(query, (day_start, day_end, inverter_serial)):
            data['data'].append({'time': row[0], 'power': row[1]})

        if self.get_datetime(date).date() == datetime.today().date():
            query = '''
                SELECT EToday
                FROM Inverters
                WHERE Serial=?;
                '''
            self.c.execute(query, (inverter_serial,))
        else:
            query = '''
                SELECT DayYield AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
                '''
            self.c.execute(query, (day_start, day_end, inverter_serial))

        res = self.c.fetchone()
        if res and res[0]: data['total'] = res[0]
        else: data['total'] = self.get_today()['inverters'][inverter_serial]['dayTotal']

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM DayData WHERE Serial=? );
            '''

        self.c.execute(query, (inverter_serial,))
        first_data, last_data = self.c.fetchone()

        if (first_data): data['hasPrevious'] = (first_data < day_start)
        else: data['hasPrevious'] = False

        if (last_data): data['hasNext'] = (last_data > day_end)
        else: data['hasNext'] = False

        # print(json.dumps(data, indent=4))
        return data

    def get_requested_month(self, date):
        data = dict()

        month_start, month_end = self.get_epoch_month(date)
        data['interval'] = {'from': self.convert_local_ts_to_utc(month_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(month_end, self.local_timezone)}
        month_total = 0

        query = '''
            SELECT TimeStamp, SUM(DayYield) AS Power
            FROM MonthData
            WHERE TimeStamp BETWEEN ? AND ?
            GROUP BY TimeStamp;
            '''

        data['data'] = list()
        for row in self.c.execute(query, (month_start, month_end)):
            data['data'].append({'time': self.convert_local_ts_to_utc(row[0], self.local_timezone), 'power': row[1]})
            month_total += row[1]

        tot_start, tot_end = self.get_epoch_tot()
        if date.split('-')[0] + '-' + date.split('-')[1] == datetime.utcfromtimestamp(tot_end).strftime('%Y-%m'):
            data['data'].append({'time': self.convert_local_ts_to_utc(tot_end, self.local_timezone), 'power': self.get_today()['dayTotal']})
            month_total += self.get_today()['dayTotal']

        data['total'] = month_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData GROUP BY TimeStamp );
            '''

        self.c.execute(query)
        first_data, last_data = self.c.fetchone()

        if first_data: data['hasPrevious'] = (first_data < month_start)
        else: data['hasPrevious'] = False
        if last_data: data['hasNext'] = (last_data > month_end)
        else: data['hasNext'] = False

        return data

    def get_requested_month_for_inverter(self, inverter_serial, date):
        data = dict()

        month_start, month_end = self.get_epoch_month(date)
        data['interval'] = {'from': self.convert_local_ts_to_utc(month_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(month_end, self.local_timezone)}
        month_total = 0

        query = '''
            SELECT TimeStamp, DayYield AS Power
            FROM MonthData
            WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
            '''

        data['data'] = list()
        for row in self.c.execute(query, (month_start, month_end, inverter_serial)):
            data['data'].append({'time': self.convert_local_ts_to_utc(row[0], self.local_timezone), 'power': row[1]})
            month_total += row[1]

        tot_start, tot_end = self.get_epoch_tot()
        if date.split('-')[0] + '-' + date.split('-')[1] == datetime.utcfromtimestamp(tot_end).strftime('%Y-%m'):
            data['data'].append({'time': self.convert_local_ts_to_utc(tot_end, self.local_timezone), 'power': self.get_today()['inverters'][inverter_serial]['dayTotal']})
            month_total += self.get_today()['inverters'][inverter_serial]['dayTotal']

        data['total'] = month_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM MonthData
            WHERE Serial=?;
            '''

        self.c.execute(query, (inverter_serial,))
        first_data, last_data = self.c.fetchone()

        if first_data: data['hasPrevious'] = (first_data < month_start)
        else: data['hasPrevious'] = False
        if last_data: data['hasNext'] = (last_data > month_end)
        else: data['hasNext'] = False

        return data

    def get_requested_year(self, date):
        data = dict()

        year_start, year_end = self.get_epoch_year(date)
        data['interval'] = {'from': self.convert_local_ts_to_utc(year_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(year_end, self.local_timezone)}

        data['data'] = list()
        month_ends = self.get_epoch_month_ends_for_year(date)

        query = '''
                SELECT SUM(DayYield) AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ?;
                '''

        current_month_start = year_start
        current_month_end = month_ends[0]

        year_total = 0
        for i in range(1, 13):
            current_month_start_local = self.convert_local_ts_to_utc(current_month_start, self.local_timezone)
            current_month_end_local = self.convert_local_ts_to_utc(current_month_end, self.local_timezone)

            self.c.execute(query, (current_month_start_local, current_month_end_local))

            gen_date = datetime(int(date.split('-')[0]), i, 1)
            month_total = self.get_requested_month(str(gen_date).split(' ')[0])['total']
            if month_total is None:
                month_total = 0

            year_total += month_total

            data['data'].append({'time': current_month_start, 'power': month_total})

            if i < 12:
                current_month_start = current_month_end+1
                current_month_end = month_ends[i]

        data['total'] = year_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData GROUP BY TimeStamp );
            '''

        self.c.execute(query)
        first_data, last_data = self.c.fetchone()

        if first_data: data['hasPrevious'] = (first_data < year_start)
        else: data['hasPrevious'] = False
        if last_data: data['hasNext'] = (last_data > year_end)
        else: data['hasNext'] = False

        return data

    def get_requested_year_for_inverter(self, inverter_serial, date):
        data = dict()

        year_start, year_end = self.get_epoch_year(date)
        data['interval'] = {'from': self.convert_local_ts_to_utc(year_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(year_end, self.local_timezone)}

        data['data'] = list()
        month_ends = self.get_epoch_month_ends_for_year(date)

        query = '''
                SELECT SUM(DayYield) AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
                '''

        current_month_start = year_start
        current_month_end = month_ends[0]

        year_total = 0
        for i in range(1, 13):
            current_month_start_local = self.convert_local_ts_to_utc(current_month_start, self.local_timezone)
            current_month_end_local = self.convert_local_ts_to_utc(current_month_end, self.local_timezone)

            self.c.execute(query, (current_month_start_local, current_month_end_local, inverter_serial))

            gen_date = datetime(int(date.split('-')[0]), i, 1)
            month_total = self.get_requested_month_for_inverter(inverter_serial, str(gen_date).split(' ')[0])['total']
            if month_total is None:
                month_total = 0

            year_total += month_total
            data['data'].append({'time': current_month_start, 'power': month_total})

            if i < 12:
                current_month_start = current_month_end+1
                current_month_end = month_ends[i]

        data['total'] = year_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData WHERE Serial=? GROUP BY TimeStamp );
            '''

        self.c.execute(query, (inverter_serial,))
        first_data, last_data = self.c.fetchone()

        if first_data: data['hasPrevious'] = (first_data < year_start)
        else: data['hasPrevious'] = False
        if last_data: data['hasNext'] = (last_data > year_end)
        else: data['hasNext'] = False

        return data

    def get_requested_tot(self):
        data = dict()

        tot_start, tot_end = self.get_epoch_tot()
        data['interval'] = {'from': self.convert_local_ts_to_utc(tot_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(tot_end, self.local_timezone)}

        string_start = datetime.utcfromtimestamp(tot_start).strftime('%Y')
        string_end = datetime.utcfromtimestamp(tot_end).strftime('%Y')

        data['data'] = list()

        for i in range(int(string_start), int(string_end) + 1):
            gen_date = str(i) + "-01-01"
            gen_ts = int(datetime(int(gen_date.split('-')[0]), 1, 1, 00, 00, 00, tzinfo=pytz.utc).timestamp())
            year = self.get_requested_year(gen_date)
            data['data'].append({'time': gen_ts, 'power': year['total']})

        return data

    def get_requested_tot_for_inverter(self, inverter_serial):
        data = dict()

        tot_start, tot_end = self.get_epoch_tot()
        data['interval'] = {'from': self.convert_local_ts_to_utc(tot_start, self.local_timezone), 'to': self.convert_local_ts_to_utc(tot_end, self.local_timezone)}

        string_start = datetime.utcfromtimestamp(tot_start).strftime('%Y')
        string_end = datetime.utcfromtimestamp(tot_end).strftime('%Y')

        data['data'] = list()

        for i in range(int(string_start), int(string_end) + 1):
            gen_date = str(i) + "-01-01"
            gen_ts = int(datetime(int(gen_date.split('-')[0]), 1, 1, 00, 00, 00, tzinfo=pytz.utc).timestamp())
            year = self.get_requested_year_for_inverter(inverter_serial, gen_date)
            data['data'].append({'time': gen_ts, 'power': year['total']})

        return data

    def get_inverters(self):
        query = '''
            SELECT Serial, Name, Type, TimeStamp, EToday, ETotal, Status, OperatingTime
            FROM Inverters;
            '''
        invs = []
        renamings = self.config.get_renamings()
        for row in self.c.execute(query):
            serial = str(row[0])
            name = row[1]
            if serial in renamings.keys():
                name = renamings[serial]

            invs.append( {
                'serial': serial,
                'name': name,
                'type': row[2],
                'ts': row[3],
                'etoday': row[4],
                'etotal': row[5],
                'status': row[6]
            } )
        return invs

    def get_local_timezone(self):
        return datetime.now(tz=pytz.utc).astimezone().tzinfo

    def convert_local_ts_to_utc(self, ts, local_timezone):
        return int(datetime.utcfromtimestamp(ts).replace(tzinfo=local_timezone).timestamp())

    def get_datetime(self, date):
        s = date.split('-')
        return datetime(int(s[0]), int(s[1]), int(s[2]), 00, 00, 00)

    def get_epoch_day(self, date):
        s = date.split('-')
        epoch_start =  int(datetime(int(s[0]), int(s[1]), int(s[2]), 00, 00, 00, tzinfo=pytz.utc).timestamp())
        epoch_end =  int(datetime(int(s[0]), int(s[1]), int(s[2]), 23, 59, 59, tzinfo=pytz.utc).timestamp())
        return epoch_start, epoch_end

    def get_epoch_month(self, date):
        s = date.split('-')
        epoch_start = int(datetime(int(s[0]), int(s[1]), 1, 00, 00, 00, tzinfo=pytz.utc).timestamp())
        epoch_end = int(datetime(int(s[0]), int(s[1]), self.get_last_day_of_month(date), 23, 59, 59, tzinfo=pytz.utc).timestamp())
        return epoch_start, epoch_end

    def get_epoch_year(self, date):
        s = date.split('-')
        epoch_start = int(datetime(int(s[0]), 1, 1, 00, 00, 00, tzinfo=pytz.utc).timestamp())
        epoch_end = int(datetime(int(s[0]), 12, 31, 23, 59, 59, tzinfo=pytz.utc).timestamp())
        return epoch_start, epoch_end

    def get_epoch_tot(self):
        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData GROUP BY TimeStamp );
            '''

        self.c.execute(query)
        epoch_start, epoch_end = self.c.fetchone()

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM DayData GROUP BY TimeStamp );
            '''

        self.c.execute(query)
        day_start, day_end = self.c.fetchone()
        if day_end > epoch_end:
            epoch_end = day_end

        return epoch_start, epoch_end

    def get_epoch_month_ends_for_year(self, date):
        s = date.split('-')
        month_ends = []
        for i in range (1,13):
            last_day_for_month = self.get_last_day_of_month(s[0] + "-" + "{:02d}".format(i) + "-" + "01")
            ts = int(datetime(int(s[0]), i, last_day_for_month, 23, 59, 59, tzinfo=pytz.utc).timestamp())
            month_ends.append(ts)
        return month_ends

    def get_last_day_of_month(self, date):
        day = datetime.strptime(date, "%Y-%m-%d")
        next_month = day.replace(day=28) + timedelta(days=4)  # this will never fail
        return (next_month - timedelta(days=next_month.day)).day

    def close(self):
        self.db.close()

if __name__ == '__main__':

    print("nothing to do here")
