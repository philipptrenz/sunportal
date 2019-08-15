#!/usr/bin/python3
"""Process SBFspot database to json format"""
import sqlite3
import util.time as time


class Database():
    """The class"""

    def __init__(self, config):
        self.config = config
        self.co2_mult = self.config.get_co2_avoidance_factor()
        self.database = sqlite3.connect(self.config.get_database_path(), check_same_thread=False)
        self.cursor = self.database.cursor()

        self.local_timezone = time.get_local_timezone()

    def get(self, date, requested_data):
        """Function called from outside"""
        tot_start, tot_end = self.get_epoch_tot()
        date_split = date.split('-')
        int_date = time.get_start_of_day(date_split[0], date_split[1], date_split[2])
        if int_date < tot_start:
            date = time.get_datestring(tot_start, '%Y-%m-%d')
        if int_date > tot_end:
            date = time.get_datestring(tot_end, '%Y-%m-%d')
        data = dict()
        data['today'] = self.get_today()
        data['requested'] = self.get_requested(date, requested_data)
        return data

    def get_today(self):
        """Process data stored in today's section"""

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

            if inv['etoday'] is not None:
                total_day += inv['etoday']
            if inv['etotal'] is not None:
                total += inv['etotal']
            co2 += inv_co2

        data['dayTotal'] = total_day
        data['total'] = total
        data['co2'] = co2

        return data

    def get_requested(self, date, requested_data):
        """Process requested data"""
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
            data['inverters'][inv['serial']] = {'day': [], 'month': [], 'year': [], 'tot': []}

            if requested_data['day'] is True:
                day_data = self.get_requested_day_for_inverter(inv['serial'], date)
                data['inverters'][inv['serial']]['day'] = day_data
            if requested_data['month'] is True:
                month_data = self.get_requested_month_for_inverter(inv['serial'], date)
                data['inverters'][inv['serial']]['month'] = month_data
            if requested_data['year'] is True:
                year_data = self.get_requested_year_for_inverter(inv['serial'], date)
                data['inverters'][inv['serial']]['year'] = year_data
            if requested_data['tot'] is True:
                tot_data = self.get_requested_tot_for_inverter(inv['serial'])
                data['inverters'][inv['serial']]['tot'] = tot_data

        return data

    def get_requested_day(self, date):
        """Process overall day data"""

        data = dict()

        day_start, day_end = time.get_epoch_day(date)
        from_ts = time.convert_local_ts_to_utc(day_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(day_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}

        query = '''
            SELECT TimeStamp, SUM(Power) AS Power
            FROM DayData
            WHERE TimeStamp BETWEEN ? AND ?
            GROUP BY TimeStamp;
        '''

        data['data'] = list()
        for row in self.cursor.execute(query, (day_start, day_end)):
            data['data'].append({'time': row[0], 'power': row[1]})


        if time.get_is_today(date):
            query = '''
                SELECT SUM(EToday) as EToday
                FROM Inverters;
                '''
            self.cursor.execute(query)
        else:
            query = '''
                SELECT SUM(DayYield) AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ?
                GROUP BY TimeStamp;
                '''
            self.cursor.execute(query, (day_start, day_end))

        row = self.cursor.fetchone()
        if row and row[0]:
            data['total'] = row[0]
        else:
            data['total'] = self.get_today()['dayTotal']


        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM DayData GROUP BY TimeStamp );
            '''

        self.cursor.execute(query)
        first_data, last_data = self.cursor.fetchone()

        if first_data:
            data['hasPrevious'] = (first_data < day_start)
        else:
            data['hasPrevious'] = False

        if last_data:
            data['hasNext'] = (last_data > day_end)
        else:
            data['hasNext'] = False

        #print(json.dumps(data, indent=4))
        return data

    def get_requested_day_for_inverter(self, inverter_serial, date):
        """Process day data per inverter"""
        data = dict()

        day_start, day_end = time.get_epoch_day(date)
        from_ts = time.convert_local_ts_to_utc(day_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(day_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}

        query = '''
            SELECT TimeStamp, Power
            FROM DayData
            WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
            '''

        data['data'] = list()
        for row in self.cursor.execute(query, (day_start, day_end, inverter_serial)):
            data['data'].append({'time': row[0], 'power': row[1]})

        if time.get_is_today(date):
            query = '''
                SELECT EToday
                FROM Inverters
                WHERE Serial=?;
                '''
            self.cursor.execute(query, (inverter_serial,))
        else:
            query = '''
                SELECT DayYield AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
                '''
            self.cursor.execute(query, (day_start, day_end, inverter_serial))

        res = self.cursor.fetchone()
        if res and res[0]:
            data['total'] = res[0]
        else:
            data['total'] = self.get_today()['inverters'][inverter_serial]['dayTotal']

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM DayData WHERE Serial=? );
            '''

        self.cursor.execute(query, (inverter_serial,))
        first_data, last_data = self.cursor.fetchone()

        if first_data:
            data['hasPrevious'] = (first_data < day_start)
        else:
            data['hasPrevious'] = False

        if last_data:
            data['hasNext'] = (last_data > day_end)
        else:
            data['hasNext'] = False

        # print(json.dumps(data, indent=4))
        return data

    def get_requested_month(self, date):
        """Process overall month data"""
        data = dict()

        month_start, month_end = time.get_epoch_month(date)
        from_ts = time.convert_local_ts_to_utc(month_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(month_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}
        month_total = 0

        query = '''
            SELECT TimeStamp, SUM(DayYield) AS Power
            FROM MonthData
            WHERE TimeStamp BETWEEN ? AND ?
            GROUP BY TimeStamp;
            '''

        data['data'] = list()
        for row in self.cursor.execute(query, (month_start, month_end)):
            time_ts = time.convert_local_ts_to_utc(row[0], self.local_timezone)
            data['data'].append({'time': time_ts, 'power': row[1]})
            month_total += row[1]

        _, tot_end = self.get_epoch_tot()
        if date.split('-')[0] + '-' + date.split('-')[1] == time.get_datestring(tot_end, '%Y-%m'):
            time_ts = time.convert_local_ts_to_utc(tot_end, self.local_timezone)
            power_over = self.get_today()['dayTotal']
            data['data'].append({'time': time_ts, 'power': power_over})
            month_total += self.get_today()['dayTotal']

        data['total'] = month_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData GROUP BY TimeStamp );
            '''

        self.cursor.execute(query)
        first_data, last_data = self.cursor.fetchone()

        if first_data:
            data['hasPrevious'] = (first_data < month_start)
        else:
            data['hasPrevious'] = False
        if last_data:
            data['hasNext'] = (last_data > month_end)
        else:
            data['hasNext'] = False

        return data

    def get_requested_month_for_inverter(self, inverter_serial, date):
        """Process month data per inverter"""
        data = dict()

        month_start, month_end = time.get_epoch_month(date)
        from_ts = time.convert_local_ts_to_utc(month_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(month_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}
        month_total = 0

        query = '''
            SELECT TimeStamp, DayYield AS Power
            FROM MonthData
            WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
            '''

        data['data'] = list()
        for row in self.cursor.execute(query, (month_start, month_end, inverter_serial)):
            time_ts = time.convert_local_ts_to_utc(row[0], self.local_timezone)
            data['data'].append({'time': time_ts, 'power': row[1]})
            month_total += row[1]

        _, tot_end = self.get_epoch_tot()
        if date.split('-')[0] + '-' + date.split('-')[1] == time.get_datestring(tot_end, '%Y-%m'):
            time_ts = time.convert_local_ts_to_utc(tot_end, self.local_timezone)
            power_inv = self.get_today()['inverters'][inverter_serial]['dayTotal']
            data['data'].append({'time': time_ts, 'power': power_inv})
            month_total += self.get_today()['inverters'][inverter_serial]['dayTotal']

        data['total'] = month_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM MonthData
            WHERE Serial=?;
            '''

        self.cursor.execute(query, (inverter_serial,))
        first_data, last_data = self.cursor.fetchone()

        if first_data:
            data['hasPrevious'] = (first_data < month_start)
        else:
            data['hasPrevious'] = False
        if last_data:
            data['hasNext'] = (last_data > month_end)
        else:
            data['hasNext'] = False

        return data

    def get_requested_year(self, date):
        """Process overall year data"""
        data = dict()

        year_start, year_end = time.get_epoch_year(date)
        from_ts = time.convert_local_ts_to_utc(year_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(year_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}

        data['data'] = list()
        month_ends = time.get_epoch_month_ends_for_year(date)

        query = '''
                SELECT SUM(DayYield) AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ?;
                '''

        month_start = year_start
        month_end = month_ends[0]

        year_total = 0
        for i in range(1, 13):
            month_start_local = time.convert_local_ts_to_utc(month_start, self.local_timezone)
            month_end_local = time.convert_local_ts_to_utc(month_end, self.local_timezone)

            self.cursor.execute(query, (month_start_local, month_end_local))

            gen_date = str(time.convert_ts_to_date(date.split('-')[0], i, 1))
            month_total = self.get_requested_month(gen_date.split(' ')[0])['total']
            if month_total is None:
                month_total = 0

            year_total += month_total

            data['data'].append({'time': month_start, 'power': month_total})

            if i < 12:
                month_start = month_end+1
                month_end = month_ends[i]

        data['total'] = year_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData GROUP BY TimeStamp );
            '''

        self.cursor.execute(query)
        first_data, last_data = self.cursor.fetchone()

        if first_data:
            data['hasPrevious'] = (first_data < year_start)
        else:
            data['hasPrevious'] = False
        if last_data:
            data['hasNext'] = (last_data > year_end)
        else:
            data['hasNext'] = False

        return data

    def get_requested_year_for_inverter(self, inverter_serial, date):
        """Process year data per inverter"""
        data = dict()

        year_start, year_end = time.get_epoch_year(date)
        from_ts = time.convert_local_ts_to_utc(year_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(year_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}

        data['data'] = list()
        month_ends = time.get_epoch_month_ends_for_year(date)

        query = '''
                SELECT SUM(DayYield) AS Power
                FROM MonthData
                WHERE TimeStamp BETWEEN ? AND ? AND Serial=?;
                '''

        month_start = year_start
        month_end = month_ends[0]

        year_total = 0
        for i in range(1, 13):
            month_start_local = time.convert_local_ts_to_utc(month_start, self.local_timezone)
            month_end_local = time.convert_local_ts_to_utc(month_end, self.local_timezone)

            self.cursor.execute(query, (month_start_local, month_end_local, inverter_serial))

            gen_date = str(time.convert_ts_to_date(date.split('-')[0], i, 1))
            out = self.get_requested_month_for_inverter(inverter_serial, gen_date.split(' ')[0])
            month_total = out['total']
            if month_total is None:
                month_total = 0

            year_total += month_total
            data['data'].append({'time': month_start, 'power': month_total})

            if i < 12:
                month_start = month_end+1
                month_end = month_ends[i]

        data['total'] = year_total

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData WHERE Serial=? GROUP BY TimeStamp );
            '''

        self.cursor.execute(query, (inverter_serial,))
        first_data, last_data = self.cursor.fetchone()

        if first_data:
            data['hasPrevious'] = (first_data < year_start)
        else:
            data['hasPrevious'] = False
        if last_data:
            data['hasNext'] = (last_data > year_end)
        else:
            data['hasNext'] = False

        return data

    def get_requested_tot(self):
        """Process overall total data"""
        data = dict()

        tot_start, tot_end = self.get_epoch_tot()
        from_ts = time.convert_local_ts_to_utc(tot_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(tot_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}

        string_start = time.get_datestring(tot_start, '%Y')
        string_end = time.get_datestring(tot_end, '%Y')

        data['data'] = list()

        for i in range(int(string_start), int(string_end) + 1):
            gen_date = str(i) + "-01-01"
            gen_timestp = time.get_start_of_day(gen_date.split('-')[0], 1, 1)
            year = self.get_requested_year(gen_date)
            data['data'].append({'time': gen_timestp, 'power': year['total']})

        return data

    def get_requested_tot_for_inverter(self, inverter_serial):
        """Process total data per inverter"""
        data = dict()

        tot_start, tot_end = self.get_epoch_tot()
        from_ts = time.convert_local_ts_to_utc(tot_start, self.local_timezone)
        to_ts = time.convert_local_ts_to_utc(tot_end, self.local_timezone)
        data['interval'] = {'from': from_ts, 'to': to_ts}

        string_start = time.get_datestring(tot_start, '%Y')
        string_end = time.get_datestring(tot_end, '%Y')

        data['data'] = list()

        for i in range(int(string_start), int(string_end) + 1):
            gen_date = str(i) + "-01-01"
            gen_timestp = time.get_start_of_day(gen_date.split('-')[0], 1, 1)
            year = self.get_requested_year_for_inverter(inverter_serial, gen_date)
            data['data'].append({'time': gen_timestp, 'power': year['total']})

        return data

    def get_inverters(self):
        """Detect inverters from database"""
        query = '''
            SELECT Serial, Name, Type, TimeStamp, EToday, ETotal, Status, OperatingTime
            FROM Inverters;
            '''
        invs = []
        renamings = self.config.get_renamings()
        for row in self.cursor.execute(query):
            serial = str(row[0])
            name = row[1]
            if serial in renamings.keys():
                name = renamings[serial]

            invs.append({
                'serial': serial,
                'name': name,
                'type': row[2],
                'ts': row[3],
                'etoday': row[4],
                'etotal': row[5],
                'status': row[6]
            })
        return invs

    def get_epoch_tot(self):
        """Detect first and last timestamp from database"""
        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM MonthData GROUP BY TimeStamp );
            '''

        self.cursor.execute(query)
        epoch_start, epoch_end = self.cursor.fetchone()

        query = '''
            SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max
            FROM ( SELECT TimeStamp FROM DayData GROUP BY TimeStamp );
            '''

        self.cursor.execute(query)
        _, day_end = self.cursor.fetchone()
        if day_end > epoch_end:
            epoch_end = day_end

        return epoch_start, epoch_end

    def close(self):
        """Close database connection"""
        self.database.close()

if __name__ == '__main__':

    print("nothing to do here")
